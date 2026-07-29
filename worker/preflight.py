"""Diagnostic préalable du worker — dit ce qui manque AVANT de lancer.

Un nouveau contributeur doit savoir en dix secondes si sa machine est prête,
plutôt que de découvrir le problème au milieu d'un téléchargement d'un gigaoctet.
"""

import shutil
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse

MIN_PYTHON = (3, 11)
MODEL_GB = 1.2

_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1", "0.0.0.0", "[::1]"}


def is_local_coordinator(url: str) -> bool:
    """Le coordinateur visé tourne-t-il sur cette machine ?

    Sert de garde-fou au mode mock : des traces simulées envoyées à un
    coordinateur public pollueraient le corpus de tout le monde.
    """
    host = (urlparse(url).hostname or "").lower()
    return host in _LOCAL_HOSTS


def check_python_version() -> tuple[bool, str]:
    version = ".".join(str(n) for n in sys.version_info[:3])
    if sys.version_info[:2] < MIN_PYTHON:
        return False, f"{version} — il en faut au moins {'.'.join(map(str, MIN_PYTHON))}"
    return True, version


def check_disk_space(path: Path, needed_gb: float = MODEL_GB) -> tuple[bool, str]:
    target = path
    while not target.exists() and target != target.parent:
        target = target.parent
    free_gb = shutil.disk_usage(target).free / 1024**3
    if free_gb < needed_gb:
        return False, f"{free_gb:.1f} Go libres, il en faut {needed_gb:.1f} Go"
    return True, f"{free_gb:.1f} Go libres"


def check_coordinator(url: str, timeout: float = 5.0) -> tuple[bool, str]:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{url} joignable"
    except OSError as exc:
        return False, f"{url} injoignable ({exc.__class__.__name__})"


def check_model(models_dir: Path, pattern: str) -> tuple[bool, str]:
    found = [p for p in models_dir.glob("*.gguf") if pattern.lower() in p.name.lower()]
    if found:
        size = found[0].stat().st_size / 1024**3
        return True, f"{found[0].name} ({size:.1f} Go)"
    return True, "sera téléchargé au premier lancement (~1,1 Go)"


def format_report(checks: list[tuple[str, bool, str]]) -> str:
    width = max(len(name) for name, _, _ in checks)
    lines = []
    for name, ok, detail in checks:
        mark = "OK   " if ok else "ÉCHEC"
        lines.append(f"  [{mark}] {name.ljust(width)}  {detail}")
    return "\n".join(lines)


def run_all(config) -> tuple[bool, str]:
    """Diagnostic complet ; renvoie (tout_va_bien, rapport lisible)."""
    checks = [
        ("Python", *check_python_version()),
        ("Espace disque", *check_disk_space(config.MODELS_DIR)),
        ("Coordinateur", *check_coordinator(config.COORDINATOR_URL)),
        ("Modèle", *check_model(config.MODELS_DIR, config.MODEL_FILE_PATTERN)),
    ]
    return all(ok for _, ok, _ in checks), format_report(checks)
