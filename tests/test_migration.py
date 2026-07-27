"""Tests du renommage Essaim → Lenyay — écrits AVANT l'implémentation (TDD).

Trois garanties : les variables LENYAY_* priment, les anciennes ESSAIM_*
restent lues avec un avertissement de dépréciation, et l'état existant
(base SQLite, identité du worker) est adopté automatiquement au premier
démarrage sous le nouveau nom. Tout tourne sur tmp_path.
"""

import importlib
import json
import sqlite3
import warnings

import pytest

import common.config as config_mod


@pytest.fixture
def reload_config(monkeypatch):
    """Recharge common.config avec l'environnement du test, puis restaure."""
    yield lambda: importlib.reload(config_mod)
    importlib.reload(config_mod)  # teardown : monkeypatch a purgé les env vars


# --- Rétrocompatibilité des variables d'environnement ----------------------


class TestRetrocompatEnv:
    def test_lenyay_prioritaire_sur_essaim(self, monkeypatch, reload_config):
        monkeypatch.setenv("LENYAY_BATCH_SIZE", "9")
        monkeypatch.setenv("ESSAIM_BATCH_SIZE", "7")
        cfg = reload_config()
        assert cfg.BATCH_SIZE == 9

    def test_fallback_essaim_avec_avertissement(self, monkeypatch, reload_config):
        monkeypatch.delenv("LENYAY_BATCH_SIZE", raising=False)
        monkeypatch.setenv("ESSAIM_BATCH_SIZE", "7")
        with pytest.warns(FutureWarning, match="ESSAIM_BATCH_SIZE"):
            cfg = reload_config()
        assert cfg.BATCH_SIZE == 7

    def test_defaut_sans_aucun_avertissement(self, monkeypatch, reload_config):
        monkeypatch.delenv("LENYAY_BATCH_SIZE", raising=False)
        monkeypatch.delenv("ESSAIM_BATCH_SIZE", raising=False)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            cfg = reload_config()
        assert cfg.BATCH_SIZE == 4

    def test_nouveaux_defauts_lenyay(self, reload_config):
        cfg = reload_config()
        assert cfg.DB_PATH.name == "lenyay.db"
        assert cfg.DEVICE_FILE.name == ".lenyay_device.json"


# --- Adoption automatique de la base au premier démarrage Lenyay ------------


class TestAdoptionDb:
    def _make_legacy_db(self, path, api_key: str) -> None:
        from coordinator import db as db_mod

        conn = sqlite3.connect(path)
        conn.executescript(db_mod._SCHEMA)
        conn.execute(
            "INSERT INTO devices (device_id, api_key, device_name, created_at, last_seen)"
            " VALUES ('d1', ?, 'ancien-appareil', 't', 't')",
            (api_key,),
        )
        conn.commit()
        conn.close()

    def test_essaim_db_adoptee_au_demarrage(self, tmp_path, monkeypatch, reload_config):
        from coordinator import db as db_mod

        legacy = tmp_path / "essaim.db"
        self._make_legacy_db(legacy, "cle-legacy")
        monkeypatch.setenv("LENYAY_DB", str(tmp_path / "lenyay.db"))
        reload_config()

        db_mod.init_db()

        assert not legacy.exists()
        assert (tmp_path / "lenyay.db").exists()
        # Les données historiques (appareils, crédits) survivent au renommage.
        device = db_mod.device_for_key("cle-legacy")
        assert device is not None and device["device_name"] == "ancien-appareil"

    def test_pas_d_adoption_si_la_nouvelle_base_existe(self, tmp_path, monkeypatch, reload_config):
        from coordinator import db as db_mod

        legacy = tmp_path / "essaim.db"
        self._make_legacy_db(legacy, "cle-legacy")
        monkeypatch.setenv("LENYAY_DB", str(tmp_path / "lenyay.db"))
        reload_config()
        db_mod.init_db()  # crée lenyay.db en adoptant

        # Un second démarrage ne doit rien re-déplacer ni écraser.
        (tmp_path / "essaim.db").touch()
        db_mod.init_db()
        assert (tmp_path / "essaim.db").exists()


# --- Adoption automatique de l'identité du worker ---------------------------


class _FakeClient:
    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key


class TestAdoptionIdentite:
    def test_essaim_device_json_adopte(self, tmp_path):
        from worker.main import _ensure_registered

        legacy = tmp_path / ".essaim_device.json"
        legacy.write_text(
            json.dumps({"device_id": "d1", "api_key": "k1", "device_name": "n1"}),
            encoding="utf-8",
        )
        client = _FakeClient()
        identity = _ensure_registered(client, tmp_path / ".lenyay_device.json")
        assert identity["device_id"] == "d1"
        assert client.api_key == "k1"
        assert not legacy.exists()
        assert (tmp_path / ".lenyay_device.json").exists()
