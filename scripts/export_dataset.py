"""Export du dataset de fine-tuning (phase 1) depuis les traces acceptées.

    .venv/Scripts/python.exe scripts/export_dataset.py [--all-traces] [--out data/exports]

Règles :
- les traces mock (« (trace simulée) ») ne sortent JAMAIS dans le dataset ;
- garde anti-contamination : toute trace dont l'énoncé figure dans le jeu
  d'éval est exclue (comparaison insensible aux espaces, comme au figeage) ;
- une trace par problème par défaut (la première acceptée) ; --all-traces
  conserve les chemins de raisonnement distincts d'un même problème ;
- sortie au format chat JSONL (system/user/assistant) avec LE prompt système
  de production (worker.inference.SYSTEM_PROMPT) — mêmes conditions
  qu'en génération et qu'à l'éval.

Lecture seule sur data/accepted/ et data/eval_set.jsonl ; n'écrit que dans
data/exports/ (ignoré par git).
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common import config  # noqa: E402
from worker.inference import SYSTEM_PROMPT  # noqa: E402

try:  # importable en module (tests) comme en script direct
    from scripts.eval import sha256_file
    from scripts.seed_eval import normalize_prompt
except ImportError:  # pragma: no cover
    from eval import sha256_file
    from seed_eval import normalize_prompt

MOCK_MARKER = "(trace simulée)"
DEFAULT_OUT_DIR = REPO_ROOT / "data" / "exports"
DEFAULT_EVAL_SET = REPO_ROOT / "data" / "eval_set.jsonl"


def load_accepted(accepted_dir: Path) -> list[dict]:
    """Toutes les traces acceptées, dans l'ordre chronologique (fichiers datés)."""
    records = []
    for path in sorted(accepted_dir.glob("*.jsonl")):
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    return records


def is_mock(record: dict) -> bool:
    return MOCK_MARKER in record["trace"]


def filter_records(
    records: list[dict],
    eval_prompts_raw: set[str],
    all_traces: bool = False,
) -> tuple[list[dict], dict]:
    """Applique les règles d'export ; renvoie (gardées, stats)."""
    eval_prompts = {normalize_prompt(p) for p in eval_prompts_raw}
    stats = {"total": len(records), "mock": 0, "eval_overlap": 0,
             "duplicates": 0, "kept": 0}
    kept: list[dict] = []
    seen: set = set()
    for record in records:
        if is_mock(record):
            stats["mock"] += 1
            continue
        if normalize_prompt(record["prompt"]) in eval_prompts:
            stats["eval_overlap"] += 1
            continue
        key = (record["task_id"], record["trace"]) if all_traces else record["task_id"]
        if key in seen:
            stats["duplicates"] += 1
            continue
        seen.add(key)
        kept.append(record)
    stats["kept"] = len(kept)
    return kept, stats


def to_chat(record: dict) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": record["prompt"]},
            {"role": "assistant", "content": record["trace"]},
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporte le dataset de fine-tuning")
    parser.add_argument("--accepted-dir", type=Path, default=config.ACCEPTED_DIR)
    parser.add_argument("--eval-set", type=Path, default=DEFAULT_EVAL_SET)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--all-traces", action="store_true",
                        help="garder les chemins de raisonnement distincts d'un même problème")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    records = load_accepted(args.accepted_dir)
    if not records:
        sys.exit(f"Aucune trace acceptée dans {args.accepted_dir}")

    eval_prompts = set()
    if args.eval_set.exists():
        with args.eval_set.open(encoding="utf-8") as f:
            eval_prompts = {json.loads(l)["prompt"] for l in f if l.strip()}

    kept, stats = filter_records(records, eval_prompts, all_traces=args.all_traces)
    if not kept:
        sys.exit("Aucune trace exportable après filtrage — dataset vide, export refusé.")

    args.out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    out_path = args.out / f"dataset-{stamp}-{len(kept)}.jsonl"
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for record in kept:
            f.write(json.dumps(to_chat(record), ensure_ascii=False) + "\n")

    print(f"Traces acceptées lues     : {stats['total']}")
    print(f"  mock écartées           : {stats['mock']}")
    print(f"  contamination éval      : {stats['eval_overlap']}")
    print(f"  doublons écartés        : {stats['duplicates']}")
    print(f"Dataset exporté           : {stats['kept']} exemples (format chat)")
    print(f"Fichier : {out_path}")
    print(f"sha256  : {sha256_file(out_path)}")


if __name__ == "__main__":
    main()
