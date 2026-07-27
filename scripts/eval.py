"""Évaluation autonome d'un modèle GGUF sur le jeu d'éval figé (GSM8K test).

Usage :
    .venv/Scripts/python.exe scripts/eval.py models/<modele>.gguf [--label nom]
                                             [--eval-set data/eval_set.jsonl]
                                             [--out-dir results] [--limit N]

Décodage strictement déterministe (température 0, seed fixe) : deux évals du
même modèle sur le même jeu donnent le même score. Le vérificateur est CELUI
du coordinateur (coordinator.verifier) — aucune logique dupliquée. Ne touche
ni la base SQLite, ni le coordinateur, ni data/tasks.jsonl.

(À venir en phase 1 : évaluation d'un adaptateur LoRA par-dessus le GGUF.)
"""

import argparse
import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from coordinator.verifier import verify  # noqa: E402  — LE vérificateur du coordinateur
from worker.inference import SYSTEM_PROMPT  # noqa: E402  — LE prompt de production

log = logging.getLogger("lenyay.eval")

# Config d'éval FIGÉE : identique pour toutes les évals à venir, sinon les
# comparaisons v0.1 vs v0.2 ne veulent rien dire.
EVAL_CONFIG = {
    "temperature": 0.0,
    "max_tokens": 640,
    "n_ctx": 2048,
    "seed": 42,
}

DEFAULT_EVAL_SET = REPO_ROOT / "data" / "eval_set.jsonl"
DEFAULT_OUT_DIR = REPO_ROOT / "results"


# --- Briques pures (testées sans modèle) -----------------------------------


def load_eval_set(path: Path) -> list[dict]:
    tasks = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                tasks.append(json.loads(line))
    return tasks


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sanitize_name(name: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in "._" else "-" for c in name.lower())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "modele"


def run_eval(
    tasks: list[dict],
    generate: Callable[[str], str],
    on_progress: Callable[[int, int, dict], None] | None = None,
) -> list[dict]:
    """Évalue chaque tâche : une seule génération (déterministe), verdict du
    vérificateur du coordinateur."""
    details = []
    for i, task in enumerate(tasks, start=1):
        trace = generate(task["prompt"])
        correct, extracted = verify(trace, task["expected_answer"])
        detail = {
            "task_id": task["task_id"],
            "expected": task["expected_answer"],
            "extracted": extracted,
            "correct": correct,
            "trace": trace,
        }
        details.append(detail)
        if on_progress is not None:
            on_progress(i, len(tasks), detail)
    return details


def summarize(details: list[dict]) -> dict:
    correct = sum(1 for d in details if d["correct"])
    total = len(details)
    return {
        "correct": correct,
        "total": total,
        "accuracy": (correct / total) if total else 0.0,
    }


def render_markdown(payload: dict) -> str:
    score = payload["score"]
    config = payload["config"]
    failures = [d for d in payload["details"] if not d["correct"]]
    lines = [
        f"# Éval {payload['model']} — {payload['date']}",
        "",
        f"**Score : {score['correct']}/{score['total']} ({score['accuracy']:.1%})**",
        "",
        f"- Jeu d'éval : sha256 `{payload['eval_set_hash'][:12]}…` "
        f"({score['total']} problèmes évalués)",
        f"- Config : température {config['temperature']}, "
        f"max_tokens {config['max_tokens']}, seed {config['seed']}",
    ]
    if payload.get("duration_seconds"):
        lines.append(f"- Durée : {payload['duration_seconds'] / 60:.1f} min")
    lines += ["", f"## Échecs ({len(failures)})", ""]
    for d in failures[:30]:
        lines.append(f"- `{d['task_id']}` : attendu {d['expected']}, extrait {d['extracted']}")
    if len(failures) > 30:
        lines.append(f"- … et {len(failures) - 30} autres (voir le JSON)")
    return "\n".join(lines) + "\n"


def append_partial(path: Path, record: dict) -> None:
    """Checkpoint au fil de l'eau : un crash à mi-éval ne perd pas tout."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_results(
    out_dir: Path, model_name: str, payload: dict, date_str: str | None = None
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = date_str or datetime.now().strftime("%Y-%m-%d-%H%M")
    stem = f"eval_{sanitize_name(model_name)}_{date_str}"
    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}.md"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, md_path


# --- Exécution réelle ------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Évalue un modèle GGUF sur le jeu figé")
    parser.add_argument("model", type=Path, help="chemin du modèle .gguf")
    parser.add_argument("--label", default=None, help="nom utilisé dans le fichier de sortie")
    parser.add_argument("--eval-set", type=Path, default=DEFAULT_EVAL_SET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--limit", type=int, default=0, help="N premiers problèmes (0 = tous)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                        datefmt="%H:%M:%S")
    # Windows : stdout redirigé vers un fichier est en cp1252 par défaut ;
    # on force l'UTF-8 pour que « > rapport.md » fonctionne toujours.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not args.model.exists():
        sys.exit(f"Modèle introuvable : {args.model}")
    if not args.eval_set.exists():
        sys.exit(f"Jeu d'éval introuvable : {args.eval_set} — lance d'abord scripts/seed_eval.py")

    tasks = load_eval_set(args.eval_set)
    if args.limit:
        tasks = tasks[: args.limit]

    eval_set_hash = sha256_file(args.eval_set)
    log.info("Hash du modèle en cours de calcul...")
    model_hash = sha256_file(args.model)

    import llama_cpp
    from llama_cpp import Llama

    log.info("Chargement du modèle %s ...", args.model.name)
    llm = Llama(
        model_path=str(args.model),
        n_ctx=EVAL_CONFIG["n_ctx"],
        seed=EVAL_CONFIG["seed"],
        verbose=False,
    )

    def generate(prompt: str) -> str:
        output = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=EVAL_CONFIG["temperature"],
            max_tokens=EVAL_CONFIG["max_tokens"],
        )
        return output["choices"][0]["message"]["content"] or ""

    label = args.label or args.model.stem
    partial_path = args.out_dir / f"eval_{sanitize_name(label)}.partial.jsonl"
    partial_path.unlink(missing_ok=True)
    running = {"correct": 0}

    def on_progress(i: int, total: int, detail: dict) -> None:
        append_partial(partial_path, detail)
        running["correct"] += int(detail["correct"])
        mark = "✓" if detail["correct"] else "✗"
        log.info("[%d/%d] %s %s (acc. courante : %.1f%%)",
                 i, total, mark, detail["task_id"], 100 * running["correct"] / i)

    log.info("Éval de %d problèmes (température 0, déterministe)...", len(tasks))
    t0 = time.time()
    details = run_eval(tasks, generate, on_progress)
    duration = time.time() - t0

    payload = {
        "model": args.model.name,
        "model_path": str(args.model),
        "model_sha256": model_hash,
        "label": label,
        "date": datetime.now(timezone.utc).isoformat(),
        "eval_set": str(args.eval_set),
        "eval_set_hash": eval_set_hash,
        "limit": args.limit or None,  # éval partielle → non comparable
        "config": {
            **EVAL_CONFIG,
            "system_prompt": SYSTEM_PROMPT,
            "llama_cpp_version": llama_cpp.__version__,
        },
        "score": summarize(details),
        "duration_seconds": round(duration, 1),
        "details": details,
    }
    json_path, md_path = write_results(args.out_dir, label, payload)
    partial_path.unlink(missing_ok=True)  # le résultat complet est écrit
    print()
    print(render_markdown(payload))
    print(f"Résultats : {json_path}\nRésumé    : {md_path}")


if __name__ == "__main__":
    main()
