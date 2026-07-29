"""Tests du chaînon manquant : une question posée sur le site, répondue par la
machine d'un membre, payée en crédits. TDD, base temporaire isolée.
"""

import importlib
import json

import pytest

import common.config as config_mod

TRACE = "Je pose le calcul etape par etape puis je verifie le total. #### {}"


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    answers = {f"t-{i:02d}": str(100 + i) for i in range(30)}
    tasks_file = tmp_path / "tasks.jsonl"
    tasks_file.write_text(
        "".join(
            json.dumps({"task_id": t, "prompt": f"p {t}", "expected_answer": a}) + "\n"
            for t, a in answers.items()
        ),
        encoding="utf-8",
    )
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
    """Fait gagner de la réputation et des crédits à un appareil."""
    tasks = client.get("/work", params={"n": n}, headers=headers).json()["tasks"]
    client.post("/results", headers=headers, json={"results": [
        {"task_id": t["task_id"], "trace": TRACE.format(answers[t["task_id"]]),
         "attempt": 1, "lease": t["lease"]} for t in tasks]})


# --- Comptes ---------------------------------------------------------------


class TestComptes:
    def test_creation_avec_credits_offerts(self, ctx):
        client, _ = ctx
        body, headers = _account(client)
        assert body["account_key"] and body["handle"] == "julien"
        me = client.get("/accounts/me", headers=headers).json()
        assert me["credits"] > 0  # de quoi essayer tout de suite

    def test_cle_inconnue_refusee(self, ctx):
        client, _ = ctx
        assert client.get("/accounts/me", headers={"X-Account-Key": "faux"}).status_code == 401

    def test_appareil_lie_alimente_le_compte(self, ctx):
        client, answers = ctx
        body, headers = _account(client)
        depart = client.get("/accounts/me", headers=headers).json()["credits"]
        device = _device(client, account_key=body["account_key"])
        _earn(client, device, answers, n=4)
        me = client.get("/accounts/me", headers=headers).json()
        assert me["credits"] > depart
        assert me["devices"][0]["credits"] > 0


# --- Poser une question ----------------------------------------------------


class TestQuestion:
    def test_poser_debite_et_met_en_attente(self, ctx):
        client, _ = ctx
        body, headers = _account(client)
        avant = client.get("/accounts/me", headers=headers).json()["credits"]
        r = client.post("/ask", headers=headers, json={"prompt": "Combien font 12 x 12 ?"})
        assert r.status_code == 200
        qid = r.json()["question_id"]
        assert r.json()["status"] == "pending"
        apres = client.get("/accounts/me", headers=headers).json()["credits"]
        assert apres == avant - r.json()["cost"]
        assert client.get(f"/ask/{qid}").json()["status"] == "pending"

    def test_sans_credit_refuse(self, ctx, monkeypatch):
        client, _ = ctx
        monkeypatch.setattr("common.config.QUESTION_COST", 10_000)
        _, headers = _account(client)
        r = client.post("/ask", headers=headers, json={"prompt": "Bonjour ?"})
        assert r.status_code == 402  # crédits insuffisants

    def test_question_demesuree_refusee(self, ctx):
        client, _ = ctx
        _, headers = _account(client)
        r = client.post("/ask", headers=headers, json={"prompt": "x" * 5000})
        assert r.status_code == 422


# --- Servir une question ---------------------------------------------------


class TestService:
    def test_seule_une_machine_eprouvee_peut_servir(self, ctx, answers=None):
        client, answers = ctx
        _, headers = _account(client)
        client.post("/ask", headers=headers, json={"prompt": "Combien font 2 + 2 ?"})
        novice = _device(client, "novice")
        assert client.get("/serve", headers=novice).json()["question"] is None
        eprouve = _device(client, "eprouve")
        _earn(client, eprouve, answers, n=4)
        assert client.get("/serve", headers=eprouve).json()["question"] is not None

    def test_boucle_complete_question_reponse(self, ctx):
        client, answers = ctx
        _, user = _account(client)
        device = _device(client, "poste-anna")
        _earn(client, device, answers, n=4)
        gains_avant = client.get("/serve", headers=device)  # réchauffe la réputation

        qid = client.post("/ask", headers=user,
                          json={"prompt": "Explique la photosynthèse."}).json()["question_id"]
        served = client.get("/serve", headers=device).json()["question"]
        assert served["id"] == qid and served["prompt"].startswith("Explique")
        # pendant le service, la question est marquée prise
        assert client.get(f"/ask/{qid}").json()["status"] == "serving"

        client.post(f"/serve/{qid}", headers=device,
                    json={"answer": "Les plantes convertissent la lumière en sucre."})
        done = client.get(f"/ask/{qid}").json()
        assert done["status"] == "done"
        assert "plantes" in done["answer"]
        assert done["device_name"] == "poste-anna"  # on sait QUI a répondu

    def test_la_machine_qui_repond_est_creditee(self, ctx):
        client, answers = ctx
        _, user = _account(client)
        owner, owner_headers = _account(client, "anna")
        device = _device(client, "poste-anna", account_key=owner["account_key"])
        _earn(client, device, answers, n=4)
        avant = client.get("/accounts/me", headers=owner_headers).json()["credits"]

        qid = client.post("/ask", headers=user, json={"prompt": "Bonjour ?"}).json()["question_id"]
        client.get("/serve", headers=device)
        client.post(f"/serve/{qid}", headers=device, json={"answer": "Bonjour !"})
        apres = client.get("/accounts/me", headers=owner_headers).json()["credits"]
        assert apres > avant  # servir rapporte plus qu'un calcul

    def test_une_question_n_est_servie_qu_une_fois(self, ctx):
        client, answers = ctx
        _, user = _account(client)
        d1 = _device(client, "un"); _earn(client, d1, answers, n=4)
        d2 = _device(client, "deux"); _earn(client, d2, answers, n=4)
        client.post("/ask", headers=user, json={"prompt": "Une seule fois ?"})
        assert client.get("/serve", headers=d1).json()["question"] is not None
        assert client.get("/serve", headers=d2).json()["question"] is None

    def test_reponse_sans_avoir_pris_la_question_refusee(self, ctx):
        client, answers = ctx
        _, user = _account(client)
        d1 = _device(client, "un"); _earn(client, d1, answers, n=4)
        d2 = _device(client, "deux"); _earn(client, d2, answers, n=4)
        qid = client.post("/ask", headers=user, json={"prompt": "A qui ?"}).json()["question_id"]
        client.get("/serve", headers=d1)
        assert client.post(f"/serve/{qid}", headers=d2,
                           json={"answer": "vol de question"}).status_code == 409
