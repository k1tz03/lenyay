"""Conversations, mémoire du fil et paliers de modèles — TDD, base isolée."""

import importlib
import json

import pytest

import common.config as config_mod

TRACE = "Je pose le calcul etape par etape puis je verifie. #### {}"


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    answers = {f"t-{i:02d}": str(100 + i) for i in range(40)}
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


def _device(client, name="poste", tier="rapide", account_key=None):
    payload = {"device_name": name, "tier": tier}
    if account_key:
        payload["account_key"] = account_key
    return {"X-API-Key": client.post("/devices/register", json=payload).json()["api_key"]}


def _earn(client, headers, answers, n=4):
    tasks = client.get("/work", params={"n": n}, headers=headers).json()["tasks"]
    client.post("/results", headers=headers, json={"results": [
        {"task_id": t["task_id"], "trace": TRACE.format(answers[t["task_id"]]),
         "attempt": 1, "lease": t["lease"]} for t in tasks]})


def _serve(client, device, answer="D'accord."):
    offer = client.get("/serve", headers=device).json()["question"]
    if offer:
        client.post(f"/serve/{offer['id']}", headers=device, json={"answer": answer})
    return offer


# --- Conversations ---------------------------------------------------------


class TestConversations:
    def test_creer_lister_supprimer(self, ctx):
        client, _ = ctx
        _, user = _account(client)
        conv = client.post("/conversations", headers=user).json()
        assert conv["id"] and conv["title"]
        listing = client.get("/conversations", headers=user).json()
        assert [c["id"] for c in listing["conversations"]] == [conv["id"]]
        client.delete(f"/conversations/{conv['id']}", headers=user)
        assert client.get("/conversations", headers=user).json()["conversations"] == []

    def test_conversation_d_autrui_inaccessible(self, ctx):
        client, _ = ctx
        _, moi = _account(client, "moi")
        _, toi = _account(client, "toi")
        conv = client.post("/conversations", headers=moi).json()
        assert client.get(f"/conversations/{conv['id']}", headers=toi).status_code == 404

    def test_titre_tire_du_premier_message(self, ctx):
        client, answers = ctx
        _, user = _account(client)
        device = _device(client); _earn(client, device, answers)
        conv = client.post("/conversations", headers=user).json()
        client.post(f"/conversations/{conv['id']}/messages", headers=user,
                    json={"prompt": "Comment planter des tomates en avril ?"})
        listing = client.get("/conversations", headers=user).json()["conversations"]
        assert "tomates" in listing[0]["title"].lower()


class TestMemoire:
    def test_le_fil_est_transmis_a_la_machine(self, ctx):
        client, answers = ctx
        _, user = _account(client)
        device = _device(client); _earn(client, device, answers)
        conv = client.post("/conversations", headers=user).json()["id"]

        client.post(f"/conversations/{conv}/messages", headers=user,
                    json={"prompt": "Je m'appelle Julien."})
        _serve(client, device, "Enchanté Julien !")
        client.post(f"/conversations/{conv}/messages", headers=user,
                    json={"prompt": "Quel est mon prénom ?"})

        offer = client.get("/serve", headers=device).json()["question"]
        roles = [m["role"] for m in offer["context"]]
        contents = " ".join(m["content"] for m in offer["context"])
        assert roles == ["user", "assistant"]  # le fil précédent, pas la question courante
        assert "Julien" in contents

    def test_les_messages_s_empilent_dans_le_fil(self, ctx):
        client, answers = ctx
        _, user = _account(client)
        device = _device(client); _earn(client, device, answers)
        conv = client.post("/conversations", headers=user).json()["id"]
        client.post(f"/conversations/{conv}/messages", headers=user, json={"prompt": "Salut"})
        _serve(client, device, "Bonjour !")
        thread = client.get(f"/conversations/{conv}", headers=user).json()["messages"]
        assert [m["role"] for m in thread] == ["user", "assistant"]
        assert thread[1]["content"] == "Bonjour !"
        assert thread[1]["device_name"] == "poste"


# --- Paliers de modèles ----------------------------------------------------


class TestPaliers:
    def test_les_paliers_sont_publies(self, ctx):
        client, _ = ctx
        tiers = client.get("/tiers").json()["tiers"]
        noms = {t["id"] for t in tiers}
        assert {"rapide", "costaud"} <= noms
        rapide = next(t for t in tiers if t["id"] == "rapide")
        costaud = next(t for t in tiers if t["id"] == "costaud")
        assert costaud["cost"] > rapide["cost"]  # plus grand modèle, plus cher

    def test_le_palier_choisi_fixe_le_prix(self, ctx):
        client, answers = ctx
        _, user = _account(client)
        conv = client.post("/conversations", headers=user).json()["id"]
        avant = client.get("/accounts/me", headers=user).json()["credits"]
        r = client.post(f"/conversations/{conv}/messages", headers=user,
                        json={"prompt": "Question difficile", "tier": "costaud"})
        assert r.json()["cost"] == config_mod.TIERS["costaud"]["cost"]
        apres = client.get("/accounts/me", headers=user).json()["credits"]
        assert apres == avant - r.json()["cost"]

    def test_une_machine_ne_sert_que_son_palier(self, ctx):
        client, answers = ctx
        _, user = _account(client)
        petite = _device(client, "petite", tier="rapide"); _earn(client, petite, answers)
        grosse = _device(client, "grosse", tier="costaud"); _earn(client, grosse, answers)
        conv = client.post("/conversations", headers=user).json()["id"]
        client.post(f"/conversations/{conv}/messages", headers=user,
                    json={"prompt": "Pour les gros bras", "tier": "costaud"})
        assert client.get("/serve", headers=petite).json()["question"] is None
        assert client.get("/serve", headers=grosse).json()["question"] is not None

    def test_servir_un_gros_palier_rapporte_davantage(self, ctx):
        client, answers = ctx
        _, user = _account(client)
        owner, owner_h = _account(client, "anna")
        grosse = _device(client, "grosse", tier="costaud", account_key=owner["account_key"])
        _earn(client, grosse, answers)
        avant = client.get("/accounts/me", headers=owner_h).json()["credits"]
        conv = client.post("/conversations", headers=user).json()["id"]
        client.post(f"/conversations/{conv}/messages", headers=user,
                    json={"prompt": "Difficile", "tier": "costaud"})
        _serve(client, grosse, "Voilà.")
        gain = client.get("/accounts/me", headers=owner_h).json()["credits"] - avant
        assert gain == config_mod.TIERS["costaud"]["reward"]


# --- Le mur de crédits -----------------------------------------------------


class TestMurDeCredits:
    def test_sans_credit_on_explique_les_deux_sorties(self, ctx, monkeypatch):
        client, _ = ctx
        _, user = _account(client)
        monkeypatch.setitem(config_mod.TIERS["rapide"], "cost", 10_000)
        conv = client.post("/conversations", headers=user).json()["id"]
        r = client.post(f"/conversations/{conv}/messages", headers=user,
                        json={"prompt": "Bonjour"})
        assert r.status_code == 402
        body = r.json()["detail"]
        assert "contribu" in body.lower()      # gagner des crédits
        assert "abonnement" in body.lower()    # ou payer
