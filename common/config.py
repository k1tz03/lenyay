"""Configuration centralisée de Lenyay — surchargeable par variables LENYAY_*.

Rétrocompatibilité : si une ancienne variable ESSAIM_* est définie (et pas sa
variante LENYAY_*), elle est lue, avec un avertissement de dépréciation.
"""

import os
import warnings
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _env(name: str, default: str) -> str:
    new_key, legacy_key = f"LENYAY_{name}", f"ESSAIM_{name}"
    if new_key in os.environ:
        return os.environ[new_key]
    if legacy_key in os.environ:
        warnings.warn(
            f"{legacy_key} est dépréciée — renomme-la en {new_key}",
            FutureWarning,
            stacklevel=2,
        )
        return os.environ[legacy_key]
    return default


# --- Réseau ----------------------------------------------------------------
COORDINATOR_URL = _env("COORDINATOR_URL", "http://127.0.0.1:8000")
HOST = _env("HOST", "127.0.0.1")
PORT = int(_env("PORT", "8000"))

# --- Chemins ---------------------------------------------------------------
DB_PATH = Path(_env("DB", str(REPO_ROOT / "data" / "lenyay.db")))
TASKS_FILE = Path(_env("TASKS", str(REPO_ROOT / "data" / "tasks.jsonl")))
ACCEPTED_DIR = Path(_env("ACCEPTED_DIR", str(REPO_ROOT / "data" / "accepted")))
DEVICE_FILE = Path(_env("DEVICE_FILE", str(REPO_ROOT / ".lenyay_device.json")))
MODELS_DIR = Path(_env("MODELS_DIR", str(REPO_ROOT / "models")))

# --- Worker ----------------------------------------------------------------
MOCK_MODE = _env("MOCK", "0") == "1"
MOCK_ACCURACY = float(_env("MOCK_ACCURACY", "0.3"))
# Borné à [1, 32] : c'est la limite acceptée par GET /work côté coordinateur.
BATCH_SIZE = min(32, max(1, int(_env("BATCH_SIZE", "4"))))
MAX_ATTEMPTS = int(_env("ATTEMPTS", "2"))
# 0 = boucle infinie ; sinon le worker s'arrête après N tâches (pratique en test).
MAX_TASKS = int(_env("MAX_TASKS", "0"))
# Mode chasse : le coordinateur sert en priorité les tâches ratées par tous.
HUNT_MODE = _env("HUNT", "0") == "1"

# --- Protections (ouverture publique) --------------------------------------
# Requêtes authentifiées par appareil et par minute.
RATE_LIMIT = int(_env("RATE_LIMIT", "120"))
# Enregistrements d'appareils par IP et par heure.
REGISTER_LIMIT = int(_env("REGISTER_LIMIT", "20"))
# Crédits maximum par appareil et par jour UTC (0 = sans plafond).
DAILY_CREDIT_CAP = int(_env("DAILY_CREDIT_CAP", "2000"))
# Une trace correcte mais plus courte que ça est jugée creuse (pas de crédit).
MIN_TRACE_CHARS = int(_env("MIN_TRACE_CHARS", "40"))

# --- Inférence -------------------------------------------------------------
TEMPERATURE = float(_env("TEMPERATURE", "0.8"))
MAX_TOKENS = int(_env("MAX_TOKENS", "640"))
MODEL_REPO = _env("MODEL_REPO", "Qwen/Qwen2.5-1.5B-Instruct-GGUF")
# On sélectionne le fichier GGUF du repo dont le nom contient ce motif.
MODEL_FILE_PATTERN = _env("MODEL_PATTERN", "q4_k_m")
