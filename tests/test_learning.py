"""Apprendre des conversations — mais seulement à travers trois portes :
consentement, retour positif, et nettoyage des données personnelles.

On refuse délibérément l'imitation brute des réponses non vérifiées (qui
provoque l'effondrement du modèle). Ces tests fixent ce contrat.
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
        yield client
    importlib.reload(config_mod)


def _register(client, email="julien@example.com", opt_in=None):
    client.post("/auth/logout")
    body = {"email": email, "password": "un-mot-de-passe-solide", "handle": "julien"}
    if opt_in is not None:
        body["learn_opt_in"] = opt_in
    return client.post("/auth/register", json=body)


def _exchange(client, prompt="Bonjour", answer="Salut à toi !"):
    """Fabrique un échange complet dans un fil et renvoie l'id du message IA."""
    from coordinator import db
    conv = client.post("/conversations").json()["id"]
    client.post(f"/conversations/{conv}/messages", json={"prompt": prompt, "tier": "rapide"})
    mid = db.add_message(conv, "assistant", answer, device_name="poste", tier="rapide")
    return conv, mid


# --- Le nettoyage des données personnelles ----------------------------------


class TestNettoyage:
    def test_efface_email_telephone_et_longues_suites_de_chiffres(self):
        from coordinator.scrub import scrub
        out = scrub("Écris à jean.dupont@gmail.com ou au 06 12 34 56 78, "
                    "carte 4539 1488 0343 6467.")
        assert "@" not in out
        assert "06 12 34 56 78" not in out and "0612345678" not in out
        assert "4539" not in out
        assert "[courriel]" in out or "[numéro]" in out

    def test_preserve_le_contenu_utile(self):
        from coordinator.scrub import scrub
        assert "photosynthèse" in scrub("Explique la photosynthèse en deux phrases.")

    def test_petits_nombres_conserves(self):
        from coordinator.scrub import scrub
        # un nombre banal n'est pas une donnée personnelle
        assert "42" in scrub("Combien font 6 fois 7 ? La réponse est 42.")


# --- Le consentement --------------------------------------------------------


class TestConsentement:
    def test_desactive_par_defaut(self, ctx):
        client = ctx
        _register(client)
        assert client.get("/accounts/me").json()["learn_opt_in"] is False

    def test_activable_a_l_inscription_puis_revocable(self, ctx):
        client = ctx
        _register(client, opt_in=True)
        assert client.get("/accounts/me").json()["learn_opt_in"] is True
        client.post("/accounts/consent", json={"opt_in": False})
        assert client.get("/accounts/me").json()["learn_opt_in"] is False

    def test_consentement_exige_une_session(self, ctx):
        client = ctx
        client.post("/auth/logout")
        assert client.post("/accounts/consent", json={"opt_in": True}).status_code == 401


# --- Le retour (👍/👎) -------------------------------------------------------


class TestRetour:
    def test_noter_une_reponse_puis_changer_d_avis(self, ctx):
        client = ctx
        _register(client)
        _, mid = _exchange(client)
        assert client.post(f"/messages/{mid}/feedback", json={"rating": "up"}).status_code == 200
        assert client.post(f"/messages/{mid}/feedback", json={"rating": "down"}).status_code == 200
        from coordinator import db
        assert db.feedback_for_message(mid) == "down"  # le dernier avis gagne

    def test_message_d_autrui_refuse(self, ctx):
        client = ctx
        _register(client, email="moi@example.com")
        _, mid = _exchange(client)
        _register(client, email="toi@example.com")  # autre session
        assert client.post(f"/messages/{mid}/feedback", json={"rating": "up"}).status_code == 404

    def test_note_invalide_refusee(self, ctx):
        client = ctx
        _register(client)
        _, mid = _exchange(client)
        assert client.post(f"/messages/{mid}/feedback",
                           json={"rating": "genial"}).status_code == 422


# --- La porte : ce qui entre dans le corpus d'apprentissage -----------------


class TestPorteApprentissage:
    def test_seuls_les_echanges_consentis_et_apprecies_sortent(self, ctx):
        client = ctx
        from coordinator import db

        # A : consent + 👍 → éligible
        _register(client, email="a@example.com", opt_in=True)
        _, mid_a = _exchange(client, "Explique la gravité.", "La gravité attire les masses.")
        client.post(f"/messages/{mid_a}/feedback", json={"rating": "up"})

        # B : consent mais 👎 → exclu
        _register(client, email="b@example.com", opt_in=True)
        _, mid_b = _exchange(client, "Truc", "Réponse ratée.")
        client.post(f"/messages/{mid_b}/feedback", json={"rating": "down"})

        # C : 👍 mais SANS consentement → exclu
        _register(client, email="c@example.com", opt_in=False)
        _, mid_c = _exchange(client, "Autre", "Bonne réponse non consentie.")
        client.post(f"/messages/{mid_c}/feedback", json={"rating": "up"})

        samples = db.learning_samples()
        textes = " ".join(s["prompt"] + " " + s["answer"] for s in samples)
        assert "gravité" in textes
        assert "ratée" not in textes
        assert "non consentie" not in textes

    def test_les_donnees_personnelles_sont_nettoyees_a_l_export(self, ctx):
        client = ctx
        from coordinator import db
        _register(client, email="a@example.com", opt_in=True)
        _, mid = _exchange(client, "Mon mail est secret@example.com",
                           "Noté, je retiens secret@example.com.")
        client.post(f"/messages/{mid}/feedback", json={"rating": "up"})
        samples = db.learning_samples()
        blob = json.dumps(samples)
        assert "secret@example.com" not in blob

    def test_un_echange_verifiable_reste_prioritaire(self, ctx):
        """Rappel de principe : le corpus vérifié (maths/code) ne dépend PAS du
        consentement ni des 👍 — il est vrai par construction. La porte ne
        concerne que les conversations libres."""
        client = ctx
        from coordinator import db
        # aucun opt-in, aucun feedback : l'export conversationnel est vide
        _register(client, email="z@example.com")
        _exchange(client)
        assert db.learning_samples() == []
