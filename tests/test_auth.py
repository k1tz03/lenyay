"""Vraie gestion de compte : e-mail, mot de passe, sessions. TDD.

Exigences de sécurité vérifiées ici : aucun mot de passe en clair nulle part,
hachage lent et salé, sessions révocables, connexion limitée en débit.
"""

import importlib
import json

import pytest

import common.config as config_mod


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    tasks_file = tmp_path / "tasks.jsonl"
    tasks_file.write_text(json.dumps(
        {"task_id": "t-00", "prompt": "p", "expected_answer": "1"}) + "\n", encoding="utf-8")
    monkeypatch.setenv("LENYAY_DB", str(tmp_path / "db.sqlite"))
    monkeypatch.setenv("LENYAY_ACCEPTED_DIR", str(tmp_path / "accepted"))
    monkeypatch.setenv("LENYAY_TASKS", str(tasks_file))
    importlib.reload(config_mod)
    from coordinator import limits
    for lim in (limits.device_limiter, limits.register_limiter, limits.public_limiter):
        lim.reset()
    from fastapi.testclient import TestClient
    from coordinator.app import app
    with TestClient(app) as client:
        yield client, tmp_path / "db.sqlite"
    importlib.reload(config_mod)


CREDS = {"email": "julien@example.com", "password": "un-mot-de-passe-solide",
         "handle": "julien"}


def _register(client, **over):
    return client.post("/auth/register", json={**CREDS, **over})


# --- Hachage ---------------------------------------------------------------


class TestHachage:
    def test_verifie_le_bon_mot_de_passe_et_refuse_les_autres(self):
        from coordinator.auth import hash_password, verify_password
        stored = hash_password("correct horse battery staple")
        assert verify_password("correct horse battery staple", stored)
        assert not verify_password("mauvais", stored)

    def test_deux_hachages_du_meme_mot_de_passe_different(self):
        """Le sel doit être unique : sinon deux comptes partageant un mot de
        passe seraient reconnaissables d'un coup d'œil dans la base."""
        from coordinator.auth import hash_password
        assert hash_password("identique") != hash_password("identique")

    def test_le_mot_de_passe_n_apparait_jamais_dans_la_base(self, ctx):
        client, db_path = ctx
        _register(client)
        contenu = db_path.read_bytes()
        assert CREDS["password"].encode() not in contenu


# --- Inscription et connexion ---------------------------------------------


class TestInscription:
    def test_inscription_ouvre_une_session(self, ctx):
        client, _ = ctx
        r = _register(client)
        assert r.status_code == 200
        assert r.json()["handle"] == "julien"
        me = client.get("/accounts/me")           # sans en-tête : le cookie suffit
        assert me.status_code == 200 and me.json()["email"] == CREDS["email"]

    def test_email_unique(self, ctx):
        client, _ = ctx
        _register(client)
        assert _register(client, handle="autre").status_code == 409

    def test_email_invalide_refuse(self, ctx):
        client, _ = ctx
        assert _register(client, email="pas-un-email").status_code == 422

    def test_mot_de_passe_trop_court_refuse(self, ctx):
        client, _ = ctx
        assert _register(client, password="court").status_code == 422


class TestConnexion:
    def test_connexion_puis_deconnexion(self, ctx):
        client, _ = ctx
        _register(client)
        client.post("/auth/logout")
        assert client.get("/accounts/me").status_code == 401
        r = client.post("/auth/login", json={"email": CREDS["email"],
                                            "password": CREDS["password"]})
        assert r.status_code == 200
        assert client.get("/accounts/me").status_code == 200

    def test_mauvais_mot_de_passe_refuse(self, ctx):
        client, _ = ctx
        _register(client); client.post("/auth/logout")
        r = client.post("/auth/login", json={"email": CREDS["email"], "password": "faux"})
        assert r.status_code == 401
        assert "identifiant" in r.json()["detail"].lower()  # ne dit pas lequel est faux

    def test_email_inconnu_repond_pareil(self, ctx):
        """Même réponse qu'un mauvais mot de passe : on ne révèle pas quels
        e-mails existent."""
        client, _ = ctx
        r = client.post("/auth/login", json={"email": "inconnu@example.com",
                                            "password": "peu importe"})
        assert r.status_code == 401 and "identifiant" in r.json()["detail"].lower()

    def test_tentatives_limitees(self, ctx, monkeypatch):
        client, _ = ctx
        _register(client); client.post("/auth/logout")
        monkeypatch.setattr("common.config.LOGIN_LIMIT", 3)
        codes = [client.post("/auth/login", json={"email": CREDS["email"],
                                                  "password": "faux"}).status_code
                 for _ in range(4)]
        assert codes[:3] == [401] * 3 and codes[3] == 429

    def test_deconnexion_invalide_la_session(self, ctx):
        client, _ = ctx
        _register(client)
        client.post("/auth/logout")
        assert client.get("/accounts/me").status_code == 401


class TestMotDePasse:
    def test_changement_de_mot_de_passe(self, ctx):
        client, _ = ctx
        _register(client)
        r = client.post("/auth/password", json={"current": CREDS["password"],
                                                "new": "un-nouveau-mot-de-passe"})
        assert r.status_code == 200
        client.post("/auth/logout")
        assert client.post("/auth/login", json={"email": CREDS["email"],
                                                "password": CREDS["password"]}).status_code == 401
        assert client.post("/auth/login", json={"email": CREDS["email"],
                                                "password": "un-nouveau-mot-de-passe"}).status_code == 200

    def test_ancien_mot_de_passe_exige(self, ctx):
        client, _ = ctx
        _register(client)
        assert client.post("/auth/password", json={"current": "faux",
                                                   "new": "un-nouveau-mot-de-passe"}).status_code == 401


# --- La clé de machine reste, mais à sa place ------------------------------


class TestCleMachine:
    def test_la_cle_sert_encore_aux_machines(self, ctx):
        client, _ = ctx
        _register(client)
        key = client.get("/accounts/me").json()["account_key"]
        assert key
        dev = client.post("/devices/register",
                          json={"device_name": "poste", "account_key": key})
        assert dev.status_code == 200

    def test_la_cle_ouvre_l_api_mais_pas_la_session(self, ctx):
        client, _ = ctx
        _register(client)
        key = client.get("/accounts/me").json()["account_key"]
        client.post("/auth/logout")
        assert client.get("/accounts/me").status_code == 401
        assert client.get("/accounts/me", headers={"X-Account-Key": key}).status_code == 200
