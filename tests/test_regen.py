"""Régénérer une réponse : même question, nouvelle machine, nouveau tirage.

Particularité Lenyay : régénérer n'est pas gratuit — l'ordinateur d'un membre
refait un vrai travail, donc le palier est débité comme pour une question.
Et la machine qui régénère ne doit PAS voir la réponse écartée, sinon elle
la répète.
"""

import importlib
import json

import pytest

import common.config as config_mod

TRACE = "Je pose le calcul etape par etape puis je verifie. #### {}"


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    answers = {f"t-{i:02d}": str(100 + i) for i in range(20)}
    tasks_file = tmp_path / "tasks.jsonl"
    tasks_file.write_text(
        "".join(json.dumps({"task_id": t, "prompt": f"p {t}", "expected_answer": a}) + "\n"
                for t, a in answers.items()), encoding="utf-8")
    monkeypatch.setenv("LENYAY_DB", str(tmp_path / "db.sqlite"))
    monkeypatch.setenv("LENYAY_ACCEPTED_DIR", str(tmp_path / "accepted"))
    monkeypatch.setenv("LENYAY_TASKS", str(tasks_file))
    monkeypatch.setenv("LENYAY_SERVE_MIN_ACCEPTED", "2")
    importlib.reload(config_mod)
    from coordinator import limits
    for lim in (limits.device_limiter, limits.register_limiter, limits.public_limiter):
        lim.reset()
    from fastapi.testclient import TestClient
    from coordinator.app import app
    with TestClient(app) as client:
        yield client, answers
    importlib.reload(config_mod)


def _login(client, email="julien@example.com"):
    client.post("/auth/logout")
    client.post("/auth/register", json={
        "email": email, "password": "un-mot-de-passe-solide", "handle": "julien"})


def _device(client, answers, name="poste"):
    key = client.post("/devices/register",
                      json={"device_name": name}).json()["api_key"]
    headers = {"X-API-Key": key}
    tasks = client.get("/work", params={"n": 4}, headers=headers).json()["tasks"]
    client.post("/results", headers=headers, json={"results": [
        {"task_id": t["task_id"], "trace": TRACE.format(answers[t["task_id"]]),
         "attempt": 1, "lease": t["lease"]} for t in tasks]})
    return headers


def _full_exchange(client, device, conv, prompt, answer):
    client.post(f"/conversations/{conv}/messages", json={"prompt": prompt, "tier": "rapide"})
    offer = client.get("/serve", headers=device).json()["question"]
    client.post(f"/serve/{offer['id']}", headers=device, json={"answer": answer})
    return offer


class TestRegenerer:
    def test_regenerer_debite_et_remet_en_file(self, ctx):
        client, answers = ctx
        _login(client)
        device = _device(client, answers)
        conv = client.post("/conversations").json()["id"]
        _full_exchange(client, device, conv, "Explique la marée.", "Réponse moyenne.")
        avant = client.get("/accounts/me").json()["credits"]
        r = client.post(f"/conversations/{conv}/regenerate", json={"tier": "rapide"})
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "pending"
        assert client.get("/accounts/me").json()["credits"] == avant - body["cost"]
        # pas de nouveau message utilisateur : on repose la MÊME question
        thread = client.get(f"/conversations/{conv}").json()["messages"]
        assert [m["role"] for m in thread] == ["user", "assistant"]

    def test_la_machine_revoit_la_question_mais_pas_la_reponse_ecartee(self, ctx):
        client, answers = ctx
        _login(client)
        device = _device(client, answers)
        conv = client.post("/conversations").json()["id"]
        _full_exchange(client, device, conv, "Je m'appelle Julien.", "Enchanté Julien !")
        _full_exchange(client, device, conv, "Explique la marée.", "Réponse à écarter.")
        client.post(f"/conversations/{conv}/regenerate", json={"tier": "rapide"})
        offer = client.get("/serve", headers=device).json()["question"]
        assert offer["prompt"] == "Explique la marée."
        contents = " ".join(m["content"] for m in offer["context"])
        assert "écarter" not in contents      # la mauvaise réponse ne biaise pas
        assert "Julien" in contents           # le début du fil, lui, reste

    def test_la_nouvelle_reponse_s_ajoute_au_fil(self, ctx):
        client, answers = ctx
        _login(client)
        device = _device(client, answers)
        conv = client.post("/conversations").json()["id"]
        _full_exchange(client, device, conv, "Explique la marée.", "Première version.")
        client.post(f"/conversations/{conv}/regenerate", json={"tier": "rapide"})
        offer = client.get("/serve", headers=device).json()["question"]
        client.post(f"/serve/{offer['id']}", headers=device,
                    json={"answer": "Seconde version, meilleure."})
        thread = client.get(f"/conversations/{conv}").json()["messages"]
        assert [m["role"] for m in thread] == ["user", "assistant", "assistant"]
        assert "Seconde" in thread[-1]["content"]

    def test_fil_sans_question_refuse(self, ctx):
        client, _ = ctx
        _login(client)
        conv = client.post("/conversations").json()["id"]
        assert client.post(f"/conversations/{conv}/regenerate",
                           json={"tier": "rapide"}).status_code == 409

    def test_fil_d_autrui_introuvable(self, ctx):
        client, answers = ctx
        _login(client, "moi@example.com")
        conv = client.post("/conversations").json()["id"]
        _login(client, "toi@example.com")
        assert client.post(f"/conversations/{conv}/regenerate",
                           json={"tier": "rapide"}).status_code == 404
