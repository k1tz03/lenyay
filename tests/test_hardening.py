"""Tests du durcissement serveur (J-9) — TDD, base temporaire isolée.

Contrat avant ouverture publique : entrées bornées, débit limité par appareil,
enregistrements limités par IP, traces creuses refusées (réponse correcte mais
sans raisonnement), plafond de crédits quotidien par appareil.
"""

import importlib
import json

import pytest

import common.config as config_mod


LONG_TRACE = "Raisonnement détaillé, étape par étape, pour vérifier le calcul. #### {}"


@pytest.fixture
def client_and_answers(tmp_path, monkeypatch):
    answers = {f"hard-{i:02d}": str(i) for i in range(6)}
    tasks_file = tmp_path / "tasks.jsonl"
    tasks_file.write_text(
        "".join(
            json.dumps({"task_id": tid, "prompt": f"p {tid}", "expected_answer": exp}) + "\n"
            for tid, exp in answers.items()
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("LENYAY_DB", str(tmp_path / "db.sqlite"))
    monkeypatch.setenv("LENYAY_ACCEPTED_DIR", str(tmp_path / "accepted"))
    monkeypatch.setenv("LENYAY_TASKS", str(tasks_file))
    monkeypatch.setenv("LENYAY_RATE_LIMIT", "5")
    monkeypatch.setenv("LENYAY_REGISTER_LIMIT", "3")
    monkeypatch.setenv("LENYAY_DAILY_CREDIT_CAP", "2")
    importlib.reload(config_mod)

    from coordinator import limits
    limits.device_limiter.reset()
    limits.register_limiter.reset()
    limits.public_limiter.reset()

    from fastapi.testclient import TestClient
    from coordinator.app import app

    with TestClient(app) as client:
        yield client, answers
    importlib.reload(config_mod)


def _register(client, name="poste"):
    response = client.post("/devices/register", json={"device_name": name})
    assert response.status_code == 200
    return {"X-API-Key": response.json()["api_key"]}


class TestBornes:
    def test_trace_demesuree_refusee(self, client_and_answers):
        client, _ = client_and_answers
        headers = _register(client)
        response = client.post("/results", headers=headers, json={
            "results": [{"task_id": "hard-00", "trace": "x" * 40_000, "attempt": 1}]})
        assert response.status_code == 422

    def test_lot_demesure_refuse(self, client_and_answers):
        client, _ = client_and_answers
        headers = _register(client)
        results = [{"task_id": "hard-00", "trace": "t", "attempt": 1}] * 65
        response = client.post("/results", headers=headers, json={"results": results})
        assert response.status_code == 422

    def test_nom_d_appareil_demesure_refuse(self, client_and_answers):
        client, _ = client_and_answers
        response = client.post("/devices/register", json={"device_name": "x" * 200})
        assert response.status_code == 422


class TestDebit:
    def test_rate_limit_par_appareil(self, client_and_answers):
        client, _ = client_and_answers
        headers = _register(client)
        codes = [client.get("/work", params={"n": 1}, headers=headers).status_code
                 for _ in range(6)]
        assert codes[:5] == [200] * 5
        assert codes[5] == 429

    def test_enregistrements_limites_par_ip(self, client_and_answers):
        client, _ = client_and_answers
        codes = [client.post("/devices/register",
                             json={"device_name": f"p{i}"}).status_code
                 for i in range(4)]
        assert codes[:3] == [200] * 3
        assert codes[3] == 429


class TestPlausibilite:
    def test_bonne_reponse_sans_raisonnement_refusee(self, client_and_answers):
        client, answers = client_and_answers
        headers = _register(client)
        response = client.post("/results", headers=headers, json={
            "results": [{"task_id": "hard-00",
                         "trace": f"#### {answers['hard-00']}", "attempt": 1}]})
        verdict = response.json()["verdicts"][0]
        assert verdict["accepted"] is False  # correcte mais creuse -> pas de crédit
        assert response.json()["credits_earned"] == 0


class TestDoS:
    def test_stats_rate_limite(self, client_and_answers, monkeypatch):
        client, _ = client_and_answers
        monkeypatch.setattr("common.config.STATS_RATE_LIMIT", 3)
        codes = [client.get("/stats").status_code for _ in range(4)]
        assert codes[:3] == [200] * 3 and codes[3] == 429

    def test_limiteur_purge_les_cles_mortes(self):
        from coordinator.limits import SlidingWindowLimiter
        lim = SlidingWindowLimiter()
        lim._PURGE_THRESHOLD = 5
        # window nulle → chaque hit est aussitôt périmé, les clés doivent partir
        for i in range(50):
            lim.allow(f"ip-{i}", limit=1, window_seconds=0.0)
        assert lim.size() <= 6  # borné, pas 50


class TestPlafondQuotidien:
    def test_credits_plafonnes_par_jour(self, client_and_answers):
        client, answers = client_and_answers
        headers = _register(client)
        earned_total = 0
        for tid in ("hard-00", "hard-01", "hard-02"):
            response = client.post("/results", headers=headers, json={
                "results": [{"task_id": tid,
                             "trace": LONG_TRACE.format(answers[tid]), "attempt": 1}]})
            body = response.json()
            earned_total += body["credits_earned"]
            # le verdict reste honnête même au-delà du plafond
            assert body["verdicts"][0]["accepted"] is True
        assert earned_total == 2  # plafond LENYAY_DAILY_CREDIT_CAP=2
