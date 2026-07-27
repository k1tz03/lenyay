"""Tests de l'export du dataset (phase 1) — écrits AVANT l'implémentation (TDD).

Contrat : ne garder que les traces réelles (jamais les mock), refuser toute
trace dont l'énoncé figure dans le jeu d'éval (anti-contamination), une trace
par problème par défaut, sortie au format chat JSONL avec LE prompt système
de production. Tout sur tmp_path.
"""

import json
from pathlib import Path

from scripts.export_dataset import (
    filter_records,
    is_mock,
    load_accepted,
    to_chat,
)
from worker.inference import SYSTEM_PROMPT


def _record(task_id: str, trace: str, prompt: str | None = None) -> dict:
    return {
        "task_id": task_id,
        "prompt": prompt or f"énoncé {task_id}",
        "expected_answer": "7",
        "trace": trace,
        "extracted_answer": "7",
        "device_id": "d1",
        "created_at": "2026-07-27T20:00:00+00:00",
    }


def _write_jsonl(path: Path, records: list[dict]) -> Path:
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )
    return path


class TestChargement:
    def test_charge_tous_les_fichiers_dans_l_ordre(self, tmp_path):
        _write_jsonl(tmp_path / "accepted-2026-07-27.jsonl", [_record("t1", "#### 7")])
        _write_jsonl(tmp_path / "accepted-2026-07-28.jsonl", [_record("t2", "#### 7")])
        records = load_accepted(tmp_path)
        assert [r["task_id"] for r in records] == ["t1", "t2"]


class TestFiltrage:
    def test_is_mock(self):
        assert is_mock(_record("t1", "(trace simulée) Je réfléchis... #### 7"))
        assert not is_mock(_record("t1", "Raisonnement réel. #### 7"))

    def test_filtre_mock_contamination_et_doublons(self):
        records = [
            _record("t1", "vraie trace A. #### 7"),
            _record("t1", "vraie trace B (autre appareil). #### 7"),  # doublon de tâche
            _record("t2", "(trace simulée) ... #### 7"),  # mock
            _record("t3", "vraie trace C. #### 7", prompt="Combien font  2 et 2 ?"),  # dans l'éval
            _record("t4", "vraie trace D. #### 7"),
        ]
        # L'énoncé de t3 contient un double espace : la comparaison doit être
        # insensible aux espaces (normalize_prompt, comme au figeage de l'éval).
        eval_prompts = {"Combien font 2 et 2 ?"}

        kept, stats = filter_records(records, eval_prompts_raw=eval_prompts)
        assert [r["task_id"] for r in kept] == ["t1", "t4"]
        assert stats == {
            "total": 5, "mock": 1, "eval_overlap": 1, "duplicates": 1, "kept": 2,
        }

    def test_all_traces_garde_les_variantes_distinctes(self):
        records = [
            _record("t1", "chemin de raisonnement A. #### 7"),
            _record("t1", "chemin de raisonnement B. #### 7"),
            _record("t1", "chemin de raisonnement A. #### 7"),  # copie exacte
        ]
        kept, stats = filter_records(records, eval_prompts_raw=set(), all_traces=True)
        assert len(kept) == 2  # A et B, la copie exacte saute
        assert stats["duplicates"] == 1


class TestFormatChat:
    def test_to_chat_utilise_le_prompt_systeme_de_production(self):
        chat = to_chat(_record("t1", "Raisonnement. #### 7", prompt="Combien ?"))
        roles = [m["role"] for m in chat["messages"]]
        assert roles == ["system", "user", "assistant"]
        assert chat["messages"][0]["content"] == SYSTEM_PROMPT
        assert chat["messages"][1]["content"] == "Combien ?"
        assert chat["messages"][2]["content"] == "Raisonnement. #### 7"
