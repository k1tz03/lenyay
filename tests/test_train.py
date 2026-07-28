"""Tests de la partie sans-GPU du script d'entraînement (validation du dataset)."""

import json

import pytest

from scripts.train_lora import load_and_validate


def _write(path, records):
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )
    return path


def _chat(user="Combien ?", assistant="#### 7"):
    return {"messages": [
        {"role": "system", "content": "s"},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]}


class TestValidation:
    def test_dataset_valide(self, tmp_path):
        path = _write(tmp_path / "ds.jsonl", [_chat(), _chat("Autre ?", "#### 9")])
        assert len(load_and_validate(path)) == 2

    def test_roles_inattendus_refuses(self, tmp_path):
        bad = {"messages": [{"role": "user", "content": "x"}]}
        path = _write(tmp_path / "ds.jsonl", [_chat(), bad])
        with pytest.raises(SystemExit):
            load_and_validate(path)

    def test_contenu_vide_refuse(self, tmp_path):
        path = _write(tmp_path / "ds.jsonl", [_chat(assistant="")])
        with pytest.raises(SystemExit):
            load_and_validate(path)

    def test_dataset_vide_refuse(self, tmp_path):
        path = tmp_path / "ds.jsonl"
        path.write_text("", encoding="utf-8")
        with pytest.raises(SystemExit):
            load_and_validate(path)
