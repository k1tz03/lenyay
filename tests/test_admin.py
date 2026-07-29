"""Administration des membres et économie du quota quotidien. TDD.

Deux règles d'argent posées par Julien :
- qui contribue ne paie jamais (ses crédits viennent de ses machines) ;
- qui ne contribue pas a droit à un minimum quotidien, pas à un usage illimité.
"""

import importlib
import json

import pytest

import common.config as config_mod

ADMIN = {"X-Admin-Token": "jeton-admin-de-test"}


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
    monkeypatch.setenv("LENYAY_ADMIN_TOKEN", ADMIN["X-Admin-Token"])
    importlib.reload(config_mod)
    from coordinator import limits
    for lim in (limits.device_limiter, limits.register_limiter, limits.public_limiter):
        lim.reset()
    from fastapi.testclient import TestClient
    from coordinator.app import app
    with TestClient(app) as client:
        yield client, answers
    importlib.reload(config_mod)


def _account(client, handle="julien", email=None):
    email = email or f"{handle}@example.com"
    client.post("/auth/logout")
    body = client.post("/auth/register", json={
        "email": email, "password": "un-mot-de-passe-solide", "handle": handle}).json()
    return body, {"X-Account-Key": body["account_key"]}


def _drain(client, headers):
    """Vide le compte en posant des questions jusqu'au 402."""
    conv = client.post("/conversations", headers=headers).json()["id"]
    for _ in range(100):
        r = client.post(f"/conversations/{conv}/messages", headers=headers,
                        json={"prompt": "encore une question", "tier": "rapide"})
        if r.status_code == 402:
            return
    raise AssertionError("le compte ne se vide jamais")


def _age_refill(account_id):
    """Fait comme si la dernière recharge datait d'hier."""
    from coordinator import db
    with db._connect() as conn:
        conn.execute("UPDATE accounts SET last_refill = '2000-01-01' WHERE account_id = ?",
                     (account_id,))


# --- La recharge quotidienne ------------------------------------------------


class TestRechargeQuotidienne:
    def test_un_compte_vide_remonte_au_plancher_le_lendemain(self, ctx):
        client, _ = ctx
        body, headers = _account(client)
        _drain(client, headers)
        assert client.get("/accounts/me", headers=headers).json()["credits"] < config_mod.TIERS["rapide"]["cost"]
        _age_refill(body["account_id"])
        me = client.get("/accounts/me", headers=headers).json()
        assert me["credits"] == config_mod.DAILY_FREE_CREDITS

    def test_pas_de_double_recharge_le_meme_jour(self, ctx):
        client, _ = ctx
        body, headers = _account(client)
        _drain(client, headers)
        _age_refill(body["account_id"])
        client.get("/accounts/me", headers=headers)
        _drain(client, headers)  # re-vide après la recharge du jour
        me = client.get("/accounts/me", headers=headers).json()
        assert me["credits"] < config_mod.DAILY_FREE_CREDITS  # pas rechargé à nouveau

    def test_la_recharge_ne_rogne_pas_un_solde_plein(self, ctx):
        client, _ = ctx
        body, headers = _account(client)
        _age_refill(body["account_id"])
        me = client.get("/accounts/me", headers=headers).json()
        assert me["credits"] == config_mod.WELCOME_CREDITS  # 20 > plancher : intact

    def test_la_recharge_est_inscrite_au_registre(self, ctx):
        client, _ = ctx
        body, headers = _account(client)
        _drain(client, headers)
        _age_refill(body["account_id"])
        client.get("/accounts/me", headers=headers)
        entries = client.get("/accounts/ledger", headers=headers).json()["entries"]
        assert entries[0]["kind"] == "daily" and entries[0]["amount"] > 0


# --- L'administration -------------------------------------------------------


class TestAccesAdmin:
    def test_sans_jeton_refuse(self, ctx):
        client, _ = ctx
        assert client.get("/admin/members").status_code == 401

    def test_mauvais_jeton_refuse(self, ctx):
        client, _ = ctx
        assert client.get("/admin/members",
                          headers={"X-Admin-Token": "faux"}).status_code == 401

    def test_administration_desactivee_sans_secret(self, ctx, monkeypatch):
        client, _ = ctx
        monkeypatch.setattr("common.config.ADMIN_TOKEN", "")
        assert client.get("/admin/members", headers=ADMIN).status_code == 403


class TestGestionMembres:
    def test_liste_complete_des_membres(self, ctx):
        client, _ = ctx
        _account(client, "julien")
        _account(client, "anna")
        members = client.get("/admin/members", headers=ADMIN).json()["members"]
        assert len(members) == 2
        anna = next(m for m in members if m["handle"] == "anna")
        assert anna["email"] == "anna@example.com"
        assert anna["credits"] == config_mod.WELCOME_CREDITS
        assert anna["banned"] is False
        assert "earned" in anna and "spent" in anna and "devices" in anna

    def test_ajuster_les_credits_avec_trace(self, ctx):
        client, _ = ctx
        body, headers = _account(client)
        r = client.post(f"/admin/members/{body['account_id']}/credits", headers=ADMIN,
                        json={"amount": 50, "reason": "geste commercial"})
        assert r.status_code == 200
        me = client.get("/accounts/me", headers=headers).json()
        assert me["credits"] == config_mod.WELCOME_CREDITS + 50
        entries = client.get("/accounts/ledger", headers=headers).json()["entries"]
        assert entries[0]["kind"] == "adjust" and "geste commercial" in entries[0]["label"]

    def test_suspendre_bloque_tout_puis_retablir(self, ctx):
        client, _ = ctx
        body, headers = _account(client)
        client.post(f"/admin/members/{body['account_id']}/ban", headers=ADMIN,
                    json={"banned": True})
        assert client.get("/accounts/me", headers=headers).status_code == 403
        conv_r = client.post("/conversations", headers=headers)
        assert conv_r.status_code == 403
        client.post(f"/admin/members/{body['account_id']}/ban", headers=ADMIN,
                    json={"banned": False})
        assert client.get("/accounts/me", headers=headers).status_code == 200

    def test_un_compte_suspendu_n_est_pas_recharge(self, ctx):
        client, _ = ctx
        body, headers = _account(client)
        _drain(client, headers)
        client.post(f"/admin/members/{body['account_id']}/ban", headers=ADMIN,
                    json={"banned": True})
        _age_refill(body["account_id"])
        client.get("/accounts/me", headers=headers)  # 403, mais surtout : pas de recharge
        client.post(f"/admin/members/{body['account_id']}/ban", headers=ADMIN,
                    json={"banned": False})
        members = client.get("/admin/members", headers=ADMIN).json()["members"]
        me = next(m for m in members if m["account_id"] == body["account_id"])
        assert me["credits"] < config_mod.DAILY_FREE_CREDITS

    def test_vue_d_ensemble(self, ctx):
        client, _ = ctx
        _, headers = _account(client)
        conv = client.post("/conversations", headers=headers).json()["id"]
        client.post(f"/conversations/{conv}/messages", headers=headers,
                    json={"prompt": "bonjour", "tier": "rapide"})
        overview = client.get("/admin/overview", headers=ADMIN).json()
        assert overview["members"] == 1
        assert overview["questions"]["pending"] == 1

    def test_la_page_admin_existe(self, ctx):
        client, _ = ctx
        r = client.get("/admin")
        assert r.status_code == 200
        assert "X-Admin-Token" in r.text  # la page demande le jeton, elle ne l'embarque pas
