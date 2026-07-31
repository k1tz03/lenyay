"""Lenyay installable (PWA) — la « version Android » du lancement."""

import importlib
import json

import pytest

import common.config as config_mod


@pytest.fixture
def client(tmp_path, monkeypatch):
    tasks_file = tmp_path / "tasks.jsonl"
    tasks_file.write_text(json.dumps(
        {"task_id": "t-00", "prompt": "p", "expected_answer": "1"}) + "\n",
        encoding="utf-8")
    monkeypatch.setenv("LENYAY_DB", str(tmp_path / "db.sqlite"))
    monkeypatch.setenv("LENYAY_ACCEPTED_DIR", str(tmp_path / "accepted"))
    monkeypatch.setenv("LENYAY_TASKS", str(tasks_file))
    importlib.reload(config_mod)
    from fastapi.testclient import TestClient
    from coordinator.app import app
    with TestClient(app) as c:
        yield c
    importlib.reload(config_mod)


class TestInstallable:
    def test_le_manifeste_est_servi_et_coherent(self, client):
        r = client.get("/static/manifest.webmanifest")
        assert r.status_code == 200
        manifest = json.loads(r.text)
        assert manifest["display"] == "standalone"
        assert manifest["start_url"] == "/"
        # chaque icône déclarée existe vraiment
        for icon in manifest["icons"]:
            assert client.get(icon["src"]).status_code == 200
        assert any(i.get("purpose") == "maskable" for i in manifest["icons"])

    def test_le_service_worker_est_a_la_racine(self, client):
        """Sous /static, il ne contrôlerait que /static — inutile."""
        r = client.get("/sw.js")
        assert r.status_code == 200
        assert "javascript" in r.headers["content-type"]
        assert "fetch" in r.text

    def test_la_page_est_branchee(self, client):
        html = client.get("/").text
        assert 'rel="manifest"' in html
        assert "serviceWorker" in html
        assert 'name="theme-color"' in html

    def test_la_banniere_de_lancement_est_la(self, client):
        html = client.get("/").text
        assert "banner.free" in html
        assert "gratuit" in html
