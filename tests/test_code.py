"""Le code comme deuxième terrain vérifiable : tests unitaires au vert = accepté.

Couvre le vérificateur sandbox (le morceau sensible : il exécute du code
produit par des machines inconnues), le catalogue mixte, la frontière de
confiance (les tests ne sortent jamais de l'API) et le palier Code du chat.
"""

import importlib
import json

import pytest

import common.config as config_mod

GOOD = """Voici la fonction demandée :

```python
def somme_pairs(nombres):
    return sum(n for n in nombres if n % 2 == 0)
```

Elle filtre puis additionne."""

BAD = """```python
def somme_pairs(nombres):
    return sum(nombres)
```"""

TESTS = (
    "assert somme_pairs([1, 2, 3, 4]) == 6\n"
    "assert somme_pairs([]) == 0\n"
    "assert somme_pairs([-2, 5]) == -2\n"
)


# --- Le vérificateur sandbox ------------------------------------------------


class TestVerificateurCode:
    def test_bonne_solution_acceptee(self):
        from coordinator.codeverify import verify_code
        accepted, detail = verify_code(GOOD, TESTS)
        assert accepted and detail == "tests:ok"

    def test_mauvaise_solution_refusee(self):
        from coordinator.codeverify import verify_code
        accepted, detail = verify_code(BAD, TESTS)
        assert not accepted

    def test_boucle_infinie_tuee(self):
        from coordinator.codeverify import verify_code
        accepted, detail = verify_code(
            "```python\ndef somme_pairs(n):\n    while True: pass\n```", TESTS)
        assert not accepted and "timeout" in (detail or "")

    def test_code_dangereux_ecarte_sans_execution(self):
        from coordinator.codeverify import verify_code
        for evil in ("import os\nos.system('echo pwned')",
                     "import subprocess",
                     "open('/etc/passwd')",
                     "__import__('socket')"):
            accepted, detail = verify_code(f"```python\n{evil}\n```", TESTS)
            assert not accepted and detail == "code:refuse", evil

    def test_sans_bloc_python_refuse_proprement(self):
        from coordinator.codeverify import verify_code
        accepted, _ = verify_code("Je ne sais pas faire.", TESTS)
        assert not accepted

    def test_exception_dans_les_tests_refusee(self):
        from coordinator.codeverify import verify_code
        accepted, _ = verify_code(
            "```python\ndef somme_pairs(n):\n    raise ValueError('non')\n```", TESTS)
        assert not accepted


# --- Le réseau : catalogue mixte et frontière de confiance -------------------


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    math = [{"task_id": f"m-{i}", "prompt": f"p {i}", "expected_answer": str(i)}
            for i in range(6)]
    code = [{"task_id": "c-01", "kind": "code",
             "prompt": "Écris somme_pairs(nombres) qui additionne les pairs.",
             "tests": TESTS}]
    tasks_file = tmp_path / "tasks.jsonl"
    tasks_file.write_text("".join(json.dumps(t) + "\n" for t in math), encoding="utf-8")
    code_file = tmp_path / "code_tasks.jsonl"
    code_file.write_text("".join(json.dumps(t) + "\n" for t in code), encoding="utf-8")
    monkeypatch.setenv("LENYAY_DB", str(tmp_path / "db.sqlite"))
    monkeypatch.setenv("LENYAY_ACCEPTED_DIR", str(tmp_path / "accepted"))
    monkeypatch.setenv("LENYAY_TASKS", str(tasks_file))
    monkeypatch.setenv("LENYAY_CODE_TASKS", str(code_file))
    monkeypatch.setenv("LENYAY_SERVE_MIN_ACCEPTED", "2")
    importlib.reload(config_mod)
    from coordinator import limits
    for lim in (limits.device_limiter, limits.register_limiter, limits.public_limiter):
        lim.reset()
    from fastapi.testclient import TestClient
    from coordinator.app import app
    with TestClient(app) as client:
        yield client


def _device(client, name="poste", tier="rapide"):
    r = client.post("/devices/register", json={"device_name": name, "tier": tier})
    return {"X-API-Key": r.json()["api_key"]}


def _grab_code_task(client, headers):
    """Tire des lots jusqu'à obtenir la tâche code du catalogue mixte."""
    for _ in range(10):
        batch = client.get("/work", params={"n": 7}, headers=headers).json()["tasks"]
        for t in batch:
            if t["task_id"] == "c-01":
                return t
    raise AssertionError("la tâche code n'est jamais servie")


class TestCatalogueMixte:
    def test_la_tache_code_est_servie_sans_ses_tests(self, ctx):
        client = ctx
        task = _grab_code_task(client, _device(client))
        assert task["kind"] == "code"
        assert "tests" not in task  # la frontière de confiance vaut aussi ici
        assert "somme_pairs" in task["prompt"]

    def test_bon_code_credite_mauvais_refuse(self, ctx):
        client = ctx
        headers = _device(client)
        task = _grab_code_task(client, headers)
        r = client.post("/results", headers=headers, json={"results": [
            {"task_id": "c-01", "attempt": 1, "lease": task["lease"], "trace": BAD}]})
        assert r.json()["verdicts"][0]["accepted"] is False
        r = client.post("/results", headers=headers, json={"results": [
            {"task_id": "c-01", "attempt": 2, "lease": task["lease"], "trace": GOOD}]})
        verdict = r.json()["verdicts"][0]
        assert verdict["accepted"] is True
        assert r.json()["credits_earned"] >= 1


class TestPaliersDisponibles:
    def test_tiers_annonce_les_machines_en_ligne(self, ctx):
        client = ctx
        _device(client, "grosse", tier="costaud")
        _device(client, "codeuse", tier="code")
        tiers = {t["id"]: t for t in client.get("/tiers").json()["tiers"]}
        assert {"rapide", "costaud", "code", "geant"} <= set(tiers)
        assert tiers["code"]["online"] == 1
        assert tiers["geant"]["online"] == 0
        # le module code se paie : nettement plus cher que costaud
        assert tiers["code"]["cost"] > tiers["costaud"]["cost"]

    def test_une_question_code_ne_va_qu_aux_machines_code(self, ctx):
        client = ctx
        client.post("/auth/register", json={
            "email": "j@example.com", "password": "un-mot-de-passe-solide",
            "handle": "julien"})
        # créditer le compte pour payer le palier code
        conv = client.post("/conversations").json()["id"]
        costaud = _device(client, "grosse", tier="costaud")
        codeuse = _device(client, "codeuse", tier="code")
        from coordinator import db
        for headers in (costaud, codeuse):
            key = headers["X-API-Key"]
            device = db.device_for_key(key)
            with db._connect() as conn:
                conn.execute(
                    "INSERT INTO rollouts (device_id, task_id, attempt, trace,"
                    " extracted_answer, accepted, created_at)"
                    " SELECT ?, 'm-' || value, 1, 'x', '1', 1, '2026-01-01'"
                    " FROM (SELECT 0 AS value UNION SELECT 1 UNION SELECT 2"
                    "       UNION SELECT 3 UNION SELECT 4)",
                    (device["device_id"],))
        r = client.post(f"/conversations/{conv}/messages",
                        json={"prompt": "Écris un tri fusion en Python.", "tier": "code"})
        assert r.status_code == 200
        assert client.get("/serve", headers=costaud).json()["question"] is None
        offered = client.get("/serve", headers=codeuse).json()["question"]
        assert offered is not None and offered["tier"] == "code"
