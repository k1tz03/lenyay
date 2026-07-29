"""Tests du mode chasse aux échecs — TDD, base temporaire isolée."""

import importlib

import pytest

import common.config as config_mod


@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setenv("LENYAY_DB", str(tmp_path / "db.sqlite"))
    importlib.reload(config_mod)
    from coordinator import db
    db.init_db()
    yield db
    importlib.reload(config_mod)


class TestHardTasks:
    def test_taches_ratees_par_tous_detectees(self, fresh_db):
        db = fresh_db
        d1, _ = db.register_device("d1")
        d2, _ = db.register_device("d2")
        # t-ratee : ratée par DEUX appareils distincts -> cible de chasse
        # (un seul appareil ne suffit pas : sinon un client hostile choisirait
        # seul ce que tout l'essaim va calculer)
        db.record_rollout(d1, "t-ratee", 1, "x", "9", accepted=False)
        db.record_rollout(d2, "t-ratee", 1, "x", "8", accepted=False)
        # t-solo : ratée par un seul appareil -> pas encore une cible
        db.record_rollout(d1, "t-solo", 1, "x", "9", accepted=False)
        # t-resolue : ratée par les deux puis résolue -> plus une cible
        db.record_rollout(d1, "t-resolue", 1, "x", "9", accepted=False)
        db.record_rollout(d2, "t-resolue", 1, "x", "7", accepted=True)
        assert db.hard_task_ids() == {"t-ratee"}


class TestSampleChasse:
    def test_priorite_aux_taches_ratees(self, fresh_db, monkeypatch):
        from coordinator import tasks as tasks_mod
        tasks_mod._tasks.clear()
        from common.schemas import TaskWithAnswer
        for tid in ("t1", "t2", "t3", "t4"):
            tasks_mod._tasks[tid] = TaskWithAnswer(
                task_id=tid, prompt=f"p {tid}", expected_answer="1")

        picked = tasks_mod.sample(2, exclude=set(), hard_first={"t3", "t2"})
        assert set(picked_ids := [t.task_id for t in picked]) == {"t2", "t3"}

        # Les cibles de chasse déjà résolues par l'appareil restent exclues.
        picked = tasks_mod.sample(3, exclude={"t3"}, hard_first={"t3", "t2"})
        ids = [t.task_id for t in picked]
        assert "t3" not in ids and ids[0] == "t2" and len(ids) == 3
