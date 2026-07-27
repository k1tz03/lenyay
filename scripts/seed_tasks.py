"""Fige 200 problèmes GSM8K dans data/tasks.jsonl (avec la réponse attendue).

À lancer UNE SEULE FOIS (le fichier généré est commité pour la reproductibilité) :

    .venv/Scripts/python.exe -m pip install -r requirements-seed.txt
    .venv/Scripts/python.exe scripts/seed_tasks.py
"""

import json
import sys
from pathlib import Path

# Lancé comme script direct : on ajoute la racine du repo pour importer common/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common import config  # noqa: E402

N_TASKS = 200


def extract_expected(gsm8k_answer: str) -> str:
    """La solution GSM8K se termine par "#### <réponse>" — on extrait et normalise."""
    raw = gsm8k_answer.split("####")[-1].strip()
    return raw.replace(",", "").replace(" ", "")


def main() -> None:
    from datasets import load_dataset

    print(f"Téléchargement de GSM8K (openai/gsm8k, split train)...")
    ds = load_dataset("openai/gsm8k", "main", split="train")

    out = config.TASKS_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, row in enumerate(ds.select(range(N_TASKS))):
            record = {
                "task_id": f"gsm8k-train-{i:04d}",
                "prompt": row["question"].strip(),
                "expected_answer": extract_expected(row["answer"]),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"{N_TASKS} tâches figées dans {out}")


if __name__ == "__main__":
    main()
