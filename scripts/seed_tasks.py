"""Fige les problèmes GSM8K (split train) dans data/tasks.jsonl, avec la réponse attendue.

Par défaut : l'intégralité du split (~7 473 problèmes). Les task_id sont dérivés
de la POSITION dans le split ("gsm8k-train-0042"), et l'ordre du split est
stable : re-seeder ne change jamais les IDs existants — les crédits et rollouts
déjà en base restent donc valides, on ne fait qu'ajouter des tâches.

    .venv/Scripts/python.exe -m pip install -r requirements-seed.txt
    .venv/Scripts/python.exe scripts/seed_tasks.py [--limit N]
"""

import argparse
import json
import sys
from pathlib import Path

# Lancé comme script direct : on ajoute la racine du repo pour importer common/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common import config  # noqa: E402


def extract_expected(gsm8k_answer: str) -> str:
    """La solution GSM8K se termine par "#### <réponse>" — on extrait et normalise."""
    raw = gsm8k_answer.split("####")[-1].strip()
    return raw.replace(",", "").replace(" ", "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fige le catalogue de tâches GSM8K")
    parser.add_argument(
        "--limit", type=int, default=0,
        help="ne garder que les N premiers problèmes (0 = tout le split)",
    )
    args = parser.parse_args()

    from datasets import load_dataset

    print("Chargement de GSM8K (openai/gsm8k, split train)...")
    ds = load_dataset("openai/gsm8k", "main", split="train")
    if args.limit:
        ds = ds.select(range(args.limit))

    out = config.TASKS_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, row in enumerate(ds):
            record = {
                "task_id": f"gsm8k-train-{i:04d}",
                "prompt": row["question"].strip(),
                "expected_answer": extract_expected(row["answer"]),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"{len(ds)} tâches figées dans {out}")


if __name__ == "__main__":
    main()
