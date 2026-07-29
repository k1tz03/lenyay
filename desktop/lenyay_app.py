"""L'application de bureau Lenyay — pour ceux qui n'ouvriront jamais un terminal.

Une fenêtre (pywebview / WebView2) qui charge le chat du coordinateur — la
page se met en « mode application » d'elle-même : chat, compte, FAQ, et un
interrupteur Contribuer. Le worker tourne en sous-processus : le MÊME
exécutable relancé avec --worker, ce qui évite d'embarquer deux programmes.

Tout ce qui appartient à l'utilisateur vit dans %APPDATA%/Lenyay :
config.json (coordinateur, clé de compte), identité de l'appareil, modèles
téléchargés, journal du worker. Désinstaller l'application n'efface pas ses
crédits : ils sont sur son compte, côté serveur.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

APP_VERSION = "0.9.0"
DEFAULT_COORDINATOR = "https://lenyay.org"

APP_DATA = Path(os.environ.get("APPDATA", str(Path.home()))) / "Lenyay"
CONFIG_FILE = APP_DATA / "config.json"
WORKER_LOG = APP_DATA / "worker.log"


def load_config() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_config(cfg: dict) -> None:
    APP_DATA.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def coordinator_url() -> str:
    return (os.environ.get("LENYAY_COORDINATOR_URL")
            or load_config().get("coordinator")
            or DEFAULT_COORDINATOR)


def _self_command() -> list[str]:
    """La commande qui relance CE programme (gelé par PyInstaller ou non)."""
    if getattr(sys, "frozen", False):
        return [sys.executable]
    return [sys.executable, os.path.abspath(__file__)]


class Api:
    """Exposée à la page via window.pywebview.api — uniquement des actions
    locales (worker, config). Aucun secret ne transite vers la page."""

    def __init__(self):
        self._proc: subprocess.Popen | None = None

    def status(self) -> dict:
        running = self._proc is not None and self._proc.poll() is None
        detail = ""
        try:
            lines = WORKER_LOG.read_text(encoding="utf-8", errors="replace").strip()
            if lines:
                detail = lines.splitlines()[-1][-120:]
        except OSError:
            pass
        return {"running": running, "detail": detail, "version": APP_VERSION}

    def start_contribute(self) -> dict:
        if self._proc is not None and self._proc.poll() is None:
            return {"running": True}
        APP_DATA.mkdir(parents=True, exist_ok=True)
        cfg = load_config()
        env = dict(os.environ)
        env.update({
            "LENYAY_COORDINATOR_URL": coordinator_url(),
            "LENYAY_DEVICE_FILE": str(APP_DATA / "device.json"),
            "LENYAY_MODELS_DIR": str(APP_DATA / "models"),
        })
        if cfg.get("account_key"):
            env["LENYAY_ACCOUNT_KEY"] = cfg["account_key"]
        if cfg.get("tier"):
            env["LENYAY_TIER"] = cfg["tier"]
        flags = 0
        if os.name == "nt":  # pas de console qui clignote chez un novice
            flags = subprocess.CREATE_NO_WINDOW
        log = open(WORKER_LOG, "a", encoding="utf-8")
        self._proc = subprocess.Popen(
            _self_command() + ["--worker"],
            env=env, stdout=log, stderr=subprocess.STDOUT, creationflags=flags,
        )
        return {"running": True}

    def stop_contribute(self) -> dict:
        if self._proc is not None and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self._proc = None
        return {"running": False}

    def set_account_key(self, key: str) -> dict:
        cfg = load_config()
        if key and cfg.get("account_key") != key:
            cfg["account_key"] = key
            save_config(cfg)
        return {"ok": True}


def run_worker() -> None:
    """Mode --worker : le vrai worker Lenyay, journalisé dans %APPDATA%."""
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                        datefmt="%H:%M:%S")
    sys.argv = ["lenyay-worker"]  # le parseur du worker ne doit pas voir --worker
    from worker.main import main as worker_main
    worker_main()


def run_gui() -> None:
    import webview  # importé ici : inutile au mode --worker

    api = Api()
    webview.create_window(
        "Lenyay", coordinator_url(), js_api=api,
        width=1120, height=780, min_size=(760, 520),
    )
    # private_mode=False : la session (cookie) survit d'un lancement à l'autre.
    webview.start(private_mode=False, storage_path=str(APP_DATA / "webview"))
    api.stop_contribute()  # fermer la fenêtre arrête proprement le worker


def main() -> None:
    parser = argparse.ArgumentParser(prog="Lenyay")
    parser.add_argument("--worker", action="store_true",
                        help="mode interne : lancer le worker de contribution")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    if args.version:
        print(f"Lenyay {APP_VERSION} — coordinateur : {coordinator_url()}")
        return
    if args.worker:
        run_worker()
        return
    run_gui()


if __name__ == "__main__":
    main()
