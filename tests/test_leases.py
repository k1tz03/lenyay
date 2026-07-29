"""Tests de la preuve de travail (bail signé) — TDD, base temporaire isolée.

Contrat : /work émet pour chaque tâche un bail HMAC lié à l'appareil ; /results
exige ce bail. Sans bail valide, aucune soumission n'est acceptée — un client
qui devine les task_id et connaît les réponses (GSM8K est public) ne peut plus
polluer le dataset sans être passé par /work.
"""

import importlib
import json
import time

import pytest

import common.config as config_mod


TRACE = "Raisonnement détaillé, étape par étape, pour vérifier le calcul. #### {}"


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    answers = {f"t-{i:02d}": str(100 + i) for i in range(8)}
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
    importlib.reload(config_mod)

    from coordinator import limits
    for lim in (limits.device_limiter, limits.register_limiter, limits.public_limiter):
        lim.reset()

    from fastapi.testclient import TestClient
    from coordinator.app import app

    with TestClient(app) as client:
        yield client, answers, tmp_path
    importlib.reload(config_mod)


def _device(client, name="poste"):
    return {"X-API-Key": client.post(
        "/devices/register", json={"device_name": name}).json()["api_key"]}


def _work(client, headers, n=1):
    return client.get("/work", params={"n": n}, headers=headers).json()["tasks"]


def _submit(client, headers, task_id, trace, lease, attempt=1):
    return client.post("/results", headers=headers, json={"results": [
        {"task_id": task_id, "trace": trace, "attempt": attempt, "lease": lease}]})


# --- Le bail ---------------------------------------------------------------


class TestBail:
    def test_work_emet_un_bail_et_jamais_la_reponse(self, ctx):
        client, _, _ = ctx
        task = _work(client, _device(client))[0]
        assert task["lease"]
        assert "expected_answer" not in task

    def test_soumission_avec_bail_valide_acceptee(self, ctx):
        client, answers, _ = ctx
        headers = _device(client)
        task = _work(client, headers)[0]
        response = _submit(client, headers, task["task_id"],
                           TRACE.format(answers[task["task_id"]]), task["lease"])
        assert response.json()["credits_earned"] == 1

    def test_sans_bail_refusee(self, ctx):
        client, answers, _ = ctx
        headers = _device(client)
        # L'attaquant devine le task_id et connaît la réponse : sans bail, rien.
        response = _submit(client, headers, "t-03", TRACE.format(answers["t-03"]), "")
        body = response.json()
        assert body["credits_earned"] == 0
        assert body["verdicts"][0]["accepted"] is False

    def test_bail_falsifie_refuse(self, ctx):
        client, answers, _ = ctx
        headers = _device(client)
        task = _work(client, headers)[0]
        forged = task["lease"][:-4] + "dead"
        response = _submit(client, headers, task["task_id"],
                           TRACE.format(answers[task["task_id"]]), forged)
        assert response.json()["credits_earned"] == 0

    def test_bail_d_un_autre_appareil_refuse(self, ctx):
        client, answers, _ = ctx
        h1, h2 = _device(client, "un"), _device(client, "deux")
        task = _work(client, h1)[0]
        # h2 rejoue le bail de h1 : lié à l'appareil, donc refusé.
        response = _submit(client, h2, task["task_id"],
                           TRACE.format(answers[task["task_id"]]), task["lease"])
        assert response.json()["credits_earned"] == 0

    def test_bail_d_une_autre_tache_refuse(self, ctx):
        client, answers, _ = ctx
        headers = _device(client)
        tasks = _work(client, headers, n=2)
        response = _submit(client, headers, tasks[0]["task_id"],
                           TRACE.format(answers[tasks[0]["task_id"]]),
                           tasks[1]["lease"])
        assert response.json()["credits_earned"] == 0

    def test_bail_expire_refuse(self, ctx, monkeypatch):
        client, answers, _ = ctx
        from coordinator import leases
        headers = _device(client)
        task = _work(client, headers)[0]
        monkeypatch.setattr(time, "time", lambda: 10**10)  # an 2286
        response = _submit(client, headers, task["task_id"],
                           TRACE.format(answers[task["task_id"]]), task["lease"])
        assert response.json()["credits_earned"] == 0

    def test_bail_valide_pour_les_tentatives_successives(self, ctx):
        client, answers, _ = ctx
        headers = _device(client)
        task = _work(client, headers)[0]
        # tentative 1 fausse, tentative 2 juste : le même bail doit servir.
        _submit(client, headers, task["task_id"], "faux raisonnement #### 999",
                task["lease"], attempt=1)
        response = _submit(client, headers, task["task_id"],
                           TRACE.format(answers[task["task_id"]]),
                           task["lease"], attempt=2)
        assert response.json()["credits_earned"] == 1

    def test_secret_persiste_entre_deux_demarrages(self, ctx):
        """Un redémarrage du coordinateur n'invalide pas les bails en cours."""
        client, answers, _ = ctx
        from coordinator import db
        first = db.server_secret()
        assert first == db.server_secret()  # stable
        assert len(first) >= 32


# --- Protection du dataset -------------------------------------------------


class TestArchiveDedup:
    def test_archive_bornee_par_tache(self, ctx, monkeypatch):
        client, answers, tmp_path = ctx
        monkeypatch.setattr("common.config.ARCHIVE_MAX_PER_TASK", 2)
        # trois appareils résolvent la même tâche : 2 traces archivées, pas 3.
        for i in range(3):
            headers = _device(client, f"poste-{i}")
            tasks = _work(client, headers, n=8)
            target = next(t for t in tasks if t["task_id"] == "t-00")
            _submit(client, headers, "t-00", TRACE.format(answers["t-00"]), target["lease"])
        lines = sum(1 for f in (tmp_path / "accepted").glob("*.jsonl")
                    for _ in f.open(encoding="utf-8"))
        assert lines == 2


# --- Plafond quotidien : plus de tâches brûlées ----------------------------


class TestPlafondNonDestructif:
    def test_plafond_atteint_renvoie_429_sans_bruler_la_tache(self, ctx, monkeypatch):
        client, answers, _ = ctx
        monkeypatch.setattr("common.config.DAILY_CREDIT_CAP", 1)
        headers = _device(client)
        tasks = _work(client, headers, n=2)
        first = _submit(client, headers, tasks[0]["task_id"],
                        TRACE.format(answers[tasks[0]["task_id"]]), tasks[0]["lease"])
        assert first.json()["credits_earned"] == 1

        # Plafond atteint : refus explicite AVANT de consommer la tâche.
        second = _submit(client, headers, tasks[1]["task_id"],
                         TRACE.format(answers[tasks[1]["task_id"]]), tasks[1]["lease"])
        assert second.status_code == 429

        # La tâche n'a pas été marquée résolue : elle reste servable demain.
        from coordinator import db
        assert tasks[1]["task_id"] not in db.accepted_task_ids(
            db.device_for_key(headers["X-API-Key"])["device_id"])
