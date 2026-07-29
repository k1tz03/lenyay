"""Registre des crédits : chaque mouvement est tracé et justifiable. TDD."""

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


def _account(client, handle="julien"):
    body = client.post("/accounts", json={"handle": handle}).json()
    return body, {"X-Account-Key": body["account_key"]}


def _device(client, name="poste", account_key=None):
    payload = {"device_name": name}
    if account_key:
        payload["account_key"] = account_key
    return {"X-API-Key": client.post("/devices/register", json=payload).json()["api_key"]}


def _earn(client, headers, answers, n=4):
    tasks = client.get("/work", params={"n": n}, headers=headers).json()["tasks"]
    client.post("/results", headers=headers, json={"results": [
        {"task_id": t["task_id"], "trace": TRACE.format(answers[t["task_id"]]),
         "attempt": 1, "lease": t["lease"]} for t in tasks]})


class TestRegistre:
    def test_les_credits_offerts_sont_inscrits(self, ctx):
        client, _ = ctx
        _, user = _account(client)
        entries = client.get("/accounts/ledger", headers=user).json()["entries"]
        assert len(entries) == 1
        assert entries[0]["kind"] == "welcome"
        assert entries[0]["amount"] == config_mod.WELCOME_CREDITS
        assert entries[0]["balance_after"] == config_mod.WELCOME_CREDITS

    def test_calculs_resolus_inscrits_avec_la_machine(self, ctx):
        client, answers = ctx
        body, user = _account(client)
        device = _device(client, "portable-anna", account_key=body["account_key"])
        _earn(client, device, answers, n=4)
        entries = client.get("/accounts/ledger", headers=user).json()["entries"]
        gains = [e for e in entries if e["kind"] == "solved"]
        assert gains and gains[0]["amount"] > 0
        assert gains[0]["device_name"] == "portable-anna"

    def test_question_posee_inscrite_en_depense(self, ctx):
        client, _ = ctx
        _, user = _account(client)
        conv = client.post("/conversations", headers=user).json()["id"]
        client.post(f"/conversations/{conv}/messages", headers=user,
                    json={"prompt": "Bonjour", "tier": "rapide"})
        entries = client.get("/accounts/ledger", headers=user).json()["entries"]
        depense = entries[0]
        assert depense["kind"] == "question" and depense["amount"] < 0
        assert "rapide" in depense["label"].lower()

    def test_reponse_servie_inscrite_en_gain(self, ctx):
        client, answers = ctx
        _, poseur = _account(client, "julien")
        anna, anna_h = _account(client, "anna")
        device = _device(client, "portable-anna", account_key=anna["account_key"])
        _earn(client, device, answers, n=4)
        conv = client.post("/conversations", headers=poseur).json()["id"]
        client.post(f"/conversations/{conv}/messages", headers=poseur, json={"prompt": "Salut"})
        offer = client.get("/serve", headers=device).json()["question"]
        client.post(f"/serve/{offer['id']}", headers=device, json={"answer": "Bonjour !"})
        entries = client.get("/accounts/ledger", headers=anna_h).json()["entries"]
        assert entries[0]["kind"] == "served" and entries[0]["amount"] > 0

    def test_le_solde_suit_les_ecritures(self, ctx):
        client, answers = ctx
        body, user = _account(client)
        device = _device(client, "poste", account_key=body["account_key"])
        _earn(client, device, answers, n=4)
        conv = client.post("/conversations", headers=user).json()["id"]
        client.post(f"/conversations/{conv}/messages", headers=user, json={"prompt": "Hey"})
        me = client.get("/accounts/me", headers=user).json()
        entries = client.get("/accounts/ledger", headers=user).json()["entries"]
        assert entries[0]["balance_after"] == me["credits"]
        assert sum(e["amount"] for e in entries) == me["credits"]

    def test_resume_gagnes_et_depenses(self, ctx):
        client, answers = ctx
        body, user = _account(client)
        device = _device(client, "poste", account_key=body["account_key"])
        _earn(client, device, answers, n=4)
        conv = client.post("/conversations", headers=user).json()["id"]
        client.post(f"/conversations/{conv}/messages", headers=user, json={"prompt": "Hey"})
        summary = client.get("/accounts/ledger", headers=user).json()["summary"]
        assert summary["earned"] > 0 and summary["spent"] > 0
        assert summary["balance"] == summary["earned"] - summary["spent"]

    def test_registre_prive(self, ctx):
        client, _ = ctx
        assert client.get("/accounts/ledger").status_code == 401
