"""Tests du dashboard et des stats enrichies — TDD, base temporaire isolée."""

import importlib
import json

import pytest

import common.config as config_mod


@pytest.fixture
def client_and_answers(tmp_path, monkeypatch):
    """TestClient du coordinateur sur base/catalogue/archive temporaires."""
    answers = {"dash-00": "7", "dash-01": "9"}
    tasks_file = tmp_path / "tasks.jsonl"
    tasks_file.write_text(
        "".join(
            json.dumps({"task_id": tid, "prompt": f"p {tid}", "expected_answer": exp})
            + "\n"
            for tid, exp in answers.items()
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("LENYAY_DB", str(tmp_path / "db.sqlite"))
    monkeypatch.setenv("LENYAY_ACCEPTED_DIR", str(tmp_path / "accepted"))
    monkeypatch.setenv("LENYAY_TASKS", str(tasks_file))
    importlib.reload(config_mod)

    from fastapi.testclient import TestClient

    from coordinator.app import app

    with TestClient(app) as client:
        yield client, answers
    importlib.reload(config_mod)


class TestStatsEnrichies:
    def test_credits_totaux_catalogue_et_derniere_activite(self, client_and_answers):
        client, answers = client_and_answers
        creds = client.post("/devices/register", json={"device_name": "poste-1"}).json()
        headers = {"X-API-Key": creds["api_key"]}
        work = client.get("/work", params={"n": 1}, headers=headers).json()
        task = work["tasks"][0]
        trace = ("Raisonnement détaillé, étape par étape, pour vérifier le calcul. "
                 f"#### {answers[task['task_id']]}")
        client.post(
            "/results",
            json={"results": [{"task_id": task["task_id"], "trace": trace,
                               "attempt": 1, "lease": task["lease"]}]},
            headers=headers,
        )

        stats = client.get("/stats").json()
        assert stats["total_credits"] == 1
        assert stats["tasks_in_catalog"] == 2
        top = stats["top_contributors"][0]
        assert top["device_name"] == "poste-1"
        assert top["last_seen"]  # horodatage ISO non vide → « dernière activité »


class TestLanding:
    def test_vitrine_publique_sur_la_racine(self, client_and_answers):
        client, _ = client_and_answers
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        # Ce qu'un visiteur doit trouver : la promesse, la preuve, la commande.
        # Le message doit porter sur le produit (une IA gratuite), pas sur la
        # mécanique interne ; et l'état réel doit être affiché sans flou.
        for marker in ("Lenyay", "IA gratuite", "datacenter", "Disponible",
                       "En construction", "--chat", "install.ps1", "install.sh",
                       "/dashboard",
                       # le produit est utilisable sur place : chat et compte
                       '"/ask"', "/accounts", "Créer un compte", "crédits"):
            assert marker in html, marker
        # La page ne doit appeler aucun service tiers.
        for tiers in ("googleapis", "gstatic", "cdn.", "googletagmanager"):
            assert tiers not in html, tiers

    def test_polices_servies_par_le_site(self, client_and_answers):
        client, _ = client_and_answers
        for name in ("familjen-latin.woff2",):
            response = client.get(f"/static/fonts/{name}")
            assert response.status_code == 200
            assert response.content[:4] == b"wOF2"


class TestDashboard:
    def test_page_lenyay_live_sans_rechargement_complet(self, client_and_answers):
        client, _ = client_and_answers
        response = client.get("/dashboard")
        assert response.status_code == 200
        html = response.text
        assert "Lenyay" in html
        assert "Essaim" not in html
        # Compteur live : fetch de /stats en JS, plus de meta-refresh plein écran.
        assert "fetch(" in html and "/stats" in html
        assert 'http-equiv="refresh"' not in html
        # Les quatre compteurs demandés et la colonne d'activité sont présents.
        for marker in ("rollouts vérifiés", "taux d'acceptation",
                       "crédits", "appareils", "Dernière activité"):
            assert marker in html, marker
