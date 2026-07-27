"""Configuration centralisée d'Essaim — tout est surchargeable par variable d'env."""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


# --- Réseau ----------------------------------------------------------------
COORDINATOR_URL = _env("ESSAIM_COORDINATOR_URL", "http://127.0.0.1:8000")
HOST = _env("ESSAIM_HOST", "127.0.0.1")
PORT = int(_env("ESSAIM_PORT", "8000"))

# --- Chemins ---------------------------------------------------------------
DB_PATH = Path(_env("ESSAIM_DB", str(REPO_ROOT / "data" / "essaim.db")))
TASKS_FILE = Path(_env("ESSAIM_TASKS", str(REPO_ROOT / "data" / "tasks.jsonl")))
ACCEPTED_DIR = Path(_env("ESSAIM_ACCEPTED_DIR", str(REPO_ROOT / "data" / "accepted")))
DEVICE_FILE = Path(_env("ESSAIM_DEVICE_FILE", str(REPO_ROOT / ".essaim_device.json")))
MODELS_DIR = Path(_env("ESSAIM_MODELS_DIR", str(REPO_ROOT / "models")))

# --- Worker ----------------------------------------------------------------
MOCK_MODE = _env("ESSAIM_MOCK", "0") == "1"
MOCK_ACCURACY = float(_env("ESSAIM_MOCK_ACCURACY", "0.3"))
BATCH_SIZE = int(_env("ESSAIM_BATCH_SIZE", "4"))
MAX_ATTEMPTS = int(_env("ESSAIM_ATTEMPTS", "2"))
# 0 = boucle infinie ; sinon le worker s'arrête après N tâches (pratique en test).
MAX_TASKS = int(_env("ESSAIM_MAX_TASKS", "0"))

# --- Inférence -------------------------------------------------------------
TEMPERATURE = float(_env("ESSAIM_TEMPERATURE", "0.8"))
MAX_TOKENS = int(_env("ESSAIM_MAX_TOKENS", "640"))
MODEL_REPO = _env("ESSAIM_MODEL_REPO", "Qwen/Qwen2.5-1.5B-Instruct-GGUF")
# On sélectionne le fichier GGUF du repo dont le nom contient ce motif.
MODEL_FILE_PATTERN = _env("ESSAIM_MODEL_PATTERN", "q4_k_m")
