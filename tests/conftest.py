"""Réglages communs des tests.

Chaque test monte son propre catalogue dans un répertoire temporaire ; le
catalogue de code RÉEL (data/code_tasks.jsonl) ne doit jamais s'y inviter.
On le pointe donc par défaut vers un fichier inexistant — les tests du
pipeline code (test_code.py) fournissent explicitement le leur.
"""

import pytest


@pytest.fixture(autouse=True)
def _isolate_code_catalog(tmp_path, monkeypatch):
    monkeypatch.setenv("LENYAY_CODE_TASKS", str(tmp_path / "no-code-tasks.jsonl"))
