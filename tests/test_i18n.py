"""L'internationalisation — six langues, zéro trou, branchée dans la page."""

import importlib
import json

import pytest

import common.config as config_mod


class TestDictionnaire:
    def test_aucune_langue_trouee(self):
        """Chaque clé existe dans chaque langue : une traduction manquante est
        un bug de build, pas une surprise d'utilisateur."""
        from coordinator import i18n
        assert i18n.missing() == []

    def test_les_six_langues(self):
        from coordinator import i18n
        assert i18n.LANGS == ["fr", "en", "es", "de", "pt", "it"]
        bundle = i18n.bundle()
        keys_fr = set(bundle["fr"])
        for lang in i18n.LANGS:
            assert set(bundle[lang]) == keys_fr, lang

    def test_la_faq_est_complete(self):
        from coordinator import i18n
        for i in range(1, 8):
            assert f"faq.q{i}" in i18n.S and f"faq.a{i}" in i18n.S

    def test_les_gabarits_gardent_leurs_variables(self):
        """Un {d} ou {c} perdu dans une traduction casserait l'affichage."""
        import re
        from coordinator import i18n
        for key, variants in i18n.S.items():
            slots = set(re.findall(r"\{\w\}", variants["fr"]))
            for lang, text in variants.items():
                assert set(re.findall(r"\{\w\}", text)) == slots, (key, lang)


@pytest.fixture
def client(tmp_path, monkeypatch):
    tasks_file = tmp_path / "tasks.jsonl"
    tasks_file.write_text(json.dumps(
        {"task_id": "t-00", "prompt": "p", "expected_answer": "1"}) + "\n",
        encoding="utf-8")
    monkeypatch.setenv("LENYAY_DB", str(tmp_path / "db.sqlite"))
    monkeypatch.setenv("LENYAY_ACCEPTED_DIR", str(tmp_path / "accepted"))
    monkeypatch.setenv("LENYAY_TASKS", str(tasks_file))
    importlib.reload(config_mod)
    from fastapi.testclient import TestClient
    from coordinator.app import app
    with TestClient(app) as c:
        yield c
    importlib.reload(config_mod)


class TestPage:
    def test_le_dictionnaire_est_embarque(self, client):
        html = client.get("/").text
        # les six langues sont dans la page, prêtes sans rechargement
        for probe in ('"en":', '"es":', '"de":', '"pt":', '"it":',
                      "applyI18n", "data-i18n", "lenyay.lang"):
            assert probe in html, probe

    def test_le_selecteur_de_langue_existe(self, client):
        html = client.get("/").text
        assert 'id="lang-pick"' in html
        for lang in ("fr", "en", "es", "de", "pt", "it"):
            assert f'value="{lang}"' in html


class TestPromptsMachines:
    def test_l_assistant_repond_dans_la_langue_de_l_utilisateur(self):
        """Les prompts de service ne doivent plus forcer le français."""
        from worker.inference import ASSISTANT_PROMPT, CODE_ASSISTANT_PROMPT
        for prompt in (ASSISTANT_PROMPT, CODE_ASSISTANT_PROMPT):
            assert "same language" in prompt
            assert "en français" not in prompt
