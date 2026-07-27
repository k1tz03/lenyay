"""Fige UNE FOIS le jeu d'évaluation : 200 problèmes du split TEST de GSM8K.

Le split test n'alimente JAMAIS l'essaim Lenyay (data/tasks.jsonl vient du train) :
c'est le jeu tenu à l'écart qui mesurera v0.1 vs v0.2. Tirage à seed fixe,
puis contrôle anti-contamination (aucun énoncé commun avec le train) affiché
avant l'écriture. Refuse d'écraser un jeu déjà figé (--force pour passer outre).

    .venv/Scripts/python.exe scripts/seed_eval.py
"""

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common import config  # noqa: E402

try:  # importable en module (tests) comme en script direct
    from scripts.seed_tasks import extract_expected
except ImportError:  # pragma: no cover
    from seed_tasks import extract_expected

DEFAULT_OUT = REPO_ROOT / "data" / "eval_set.jsonl"
N_EVAL = 200
SEED = 42


def pick_indices(n: int, total: int, seed: int) -> list[int]:
    """Tirage sans remise, déterministe, trié (les IDs suivent l'ordre du split)."""
    return sorted(random.Random(seed).sample(range(total), n))


def normalize_prompt(prompt: str) -> str:
    return " ".join(prompt.split())


def check_contamination(records: list[dict], tasks_path: Path) -> list[str]:
    """IDs des problèmes d'éval dont l'énoncé figure aussi dans le catalogue
    d'entraînement (comparaison insensible aux espaces)."""
    train_prompts = set()
    with tasks_path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                train_prompts.add(normalize_prompt(json.loads(line)["prompt"]))
    return [
        r["task_id"] for r in records if normalize_prompt(r["prompt"]) in train_prompts
    ]


def write_eval_set(records: list[dict], out_path: Path, force: bool = False) -> None:
    if out_path.exists() and not force:
        raise RuntimeError(
            f"{out_path} existe déjà : le jeu d'éval est figé UNE FOIS. "
            "(--force pour le régénérer, ce qui invalide les évals passées.)"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" : le sha256 du jeu figé doit identifier le CONTENU, pas les
    # fins de ligne de la plateforme (CRLF Windows vs LF du blob git).
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fige le jeu d'évaluation GSM8K (split test)")
    parser.add_argument("--n", type=int, default=N_EVAL)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    from datasets import load_dataset

    print("Chargement de GSM8K (openai/gsm8k, split TEST)...")
    ds = load_dataset("openai/gsm8k", "main", split="test")
    indices = pick_indices(args.n, len(ds), args.seed)
    records = []
    for i in indices:
        row = ds[i]
        records.append({
            "task_id": f"gsm8k-test-{i:04d}",
            "prompt": row["question"].strip(),
            "expected_answer": extract_expected(row["answer"]),
        })

    contaminated = check_contamination(records, config.TASKS_FILE)
    if contaminated:
        print(f"CONTAMINATION DÉTECTÉE — {len(contaminated)} problème(s) d'éval "
              f"présents dans {config.TASKS_FILE} : {contaminated[:5]}...")
        sys.exit(2)
    print(f"Contrôle anti-contamination : OK — aucun des {len(records)} problèmes "
          f"d'éval ne figure dans {config.TASKS_FILE.name} "
          f"({sum(1 for _ in config.TASKS_FILE.open(encoding='utf-8'))} tâches d'entraînement).")

    write_eval_set(records, args.out, force=args.force)

    from scripts.eval import sha256_file  # import tardif pour rester léger

    print(f"{len(records)} problèmes figés dans {args.out}")
    print(f"sha256 : {sha256_file(args.out)}")


if __name__ == "__main__":
    main()
