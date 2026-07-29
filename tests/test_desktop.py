"""La coquille de bureau — les parties testables sans fenêtre.

Le bug qu'on verrouille ici : la coquille importait un point d'entrée du
worker qui n'existait pas, et seul le test de l'exécutable compilé l'a vu.
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _reload_app(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    import desktop.lenyay_app as app
    return importlib.reload(app)


class TestCoquille:
    def test_le_point_d_entree_du_worker_existe(self):
        """L'import que fait run_worker() doit rester valide."""
        from worker.main import run
        assert callable(run)

    def test_config_aller_retour(self, tmp_path, monkeypatch):
        app = _reload_app(tmp_path, monkeypatch)
        app.save_config({"coordinator": "https://exemple.org"})
        assert app.load_config()["coordinator"] == "https://exemple.org"
        assert app.coordinator_url() == "https://exemple.org"

    def test_la_cle_de_compte_est_persistee(self, tmp_path, monkeypatch):
        app = _reload_app(tmp_path, monkeypatch)
        app.Api().set_account_key("lny_abc")
        assert app.load_config()["account_key"] == "lny_abc"

    def test_config_absente_ou_corrompue_ne_casse_rien(self, tmp_path, monkeypatch):
        app = _reload_app(tmp_path, monkeypatch)
        assert app.load_config() == {}
        app.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        app.CONFIG_FILE.write_text("{pas du json", encoding="utf-8")
        assert app.load_config() == {}
        assert app.coordinator_url() == app.DEFAULT_COORDINATOR

    def test_status_sans_worker(self, tmp_path, monkeypatch):
        app = _reload_app(tmp_path, monkeypatch)
        status = app.Api().status()
        assert status["running"] is False and "version" in status

    def test_la_commande_de_relance_pointe_sur_le_script(self, tmp_path, monkeypatch):
        app = _reload_app(tmp_path, monkeypatch)
        command = app._self_command()
        assert command[0] == sys.executable
        assert command[-1].endswith("lenyay_app.py")
