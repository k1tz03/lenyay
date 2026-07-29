"""Tests du second tour de durcissement (revue adversariale de la preuve de travail).

Contrats visés :
- l'archive n'est plus attribuée « au premier arrivé » : la sélection des
  traces du dataset se fait à l'export, avec tout le corpus en main ;
- toute soumission compte au quota (pas seulement les acceptées) : plus
  d'écriture disque illimitée en soumettant exprès des réponses fausses ;
- le nombre de tentatives par tâche est compté par le serveur, pas déclaré
  par le client (fin du rejeu infini d'un bail et de la pondération truquée) ;
- un bail malformé ou non-ASCII ne fait pas tomber la requête ;
- le mode chasse exige plusieurs appareils distincts en échec.
"""

import importlib
import json

import pytest

import common.config as config_mod

TRACE = "Raisonnement détaillé, étape par étape, pour vérifier le calcul. #### {}"


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    answers = {f"t-{i:02d}": str(100 + i) for i in range(10)}
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


def _post(client, headers, items):
    return client.post("/results", headers=headers, json={"results": items})


class TestQuotaToutesSoumissions:
    def test_mauvaises_reponses_comptees_au_quota(self, ctx, monkeypatch):
        client, _, _ = ctx
        monkeypatch.setattr("common.config.DAILY_SUBMISSION_CAP", 3)
        headers = _device(client)
        tasks = _work(client, headers, n=6)
        # Que des réponses fausses : elles ne rapportent rien mais écrivent.
        for task in tasks[:3]:
            _post(client, headers, [{"task_id": task["task_id"], "trace": "faux #### 1",
                                     "attempt": 1, "lease": task["lease"]}])
        blocked = _post(client, headers, [{"task_id": tasks[3]["task_id"],
                                           "trace": "faux #### 1", "attempt": 1,
                                           "lease": tasks[3]["lease"]}])
        assert blocked.status_code == 429


class TestTentativesCoteServeur:
    def test_rejeu_du_meme_bail_borne(self, ctx, monkeypatch):
        client, answers, _ = ctx
        monkeypatch.setattr("common.config.MAX_ATTEMPTS_PER_TASK", 3)
        headers = _device(client)
        task = _work(client, headers)[0]
        item = {"task_id": task["task_id"], "trace": "faux #### 1",
                "attempt": 1, "lease": task["lease"]}
        for _ in range(3):
            _post(client, headers, [item])
        # Au-delà, la soumission est refusée : plus d'écriture possible.
        response = _post(client, headers, [item])
        assert response.json()["verdicts"][0]["accepted"] is False
        from coordinator import db
        device_id = db.device_for_key(headers["X-API-Key"])["device_id"]
        assert db.attempts_for_task(device_id, task["task_id"]) == 3

    def test_attempt_derive_par_le_serveur(self, ctx):
        client, answers, _ = ctx
        headers = _device(client)
        task = _work(client, headers)[0]
        # Le client prétend attempt=32 (pondération d'entraînement truquée).
        response = _post(client, headers, [{
            "task_id": task["task_id"], "trace": TRACE.format(answers[task["task_id"]]),
            "attempt": 32, "lease": task["lease"]}])
        assert response.json()["verdicts"][0]["attempt"] == 1  # recompté


class TestBailRobuste:
    def test_bail_non_ascii_ne_casse_pas_la_requete(self, ctx, answers=None):
        client, answers, _ = ctx
        headers = _device(client)
        response = _post(client, headers, [{
            "task_id": "t-00", "trace": TRACE.format(answers["t-00"]),
            "attempt": 1, "lease": "9999999999." + "é" * 32}])
        assert response.status_code == 200
        assert response.json()["verdicts"][0]["accepted"] is False

    @pytest.mark.parametrize("lease", ["", ".", "abc", "1_0.deadbeef", " 99.aa", "٩٩.aa"])
    def test_bails_degeneres_refuses_sans_erreur(self, ctx, lease):
        client, answers, _ = ctx
        headers = _device(client)
        response = _post(client, headers, [{
            "task_id": "t-00", "trace": TRACE.format(answers["t-00"]),
            "attempt": 1, "lease": lease}])
        assert response.status_code == 200
        assert response.json()["credits_earned"] == 0


class TestChasseNonDetournable:
    def test_une_seule_source_ne_suffit_pas_a_marquer_dur(self, ctx, monkeypatch):
        client, _, _ = ctx
        monkeypatch.setattr("common.config.HARD_MIN_DEVICES", 2)
        from coordinator import db
        h1 = _device(client, "un")
        tasks = _work(client, h1, n=2)
        _post(client, h1, [{"task_id": tasks[0]["task_id"], "trace": "faux #### 1",
                            "attempt": 1, "lease": tasks[0]["lease"]}])
        assert db.hard_task_ids() == set()  # un seul appareil : insuffisant

        h2 = _device(client, "deux")
        t2 = next(t for t in _work(client, h2, n=10)
                  if t["task_id"] == tasks[0]["task_id"])
        _post(client, h2, [{"task_id": t2["task_id"], "trace": "faux #### 1",
                            "attempt": 1, "lease": t2["lease"]}])
        assert db.hard_task_ids() == {tasks[0]["task_id"]}


class TestExportSelection:
    def test_export_borne_les_traces_par_tache(self, tmp_path):
        from scripts.export_dataset import filter_records

        def rec(task_id, device, trace):
            return {"task_id": task_id, "prompt": f"p {task_id}", "expected_answer": "7",
                    "trace": trace, "extracted_answer": "7", "device_id": device,
                    "attempt": 1, "created_at": "2026-07-29T12:00:00+00:00"}

        records = [rec("t1", f"d{i}", f"raisonnement variante {i} #### 7") for i in range(6)]
        records += [rec("t1", "d9", "raisonnement variante 0 #### 7")]  # copie exacte
        kept, stats = filter_records(records, eval_prompts_raw=set(),
                                     all_traces=True, max_per_task=3)
        assert len(kept) == 3
        assert stats["over_task_quota"] == 3
        assert stats["duplicates"] == 1  # la copie exacte, écartée en amont
