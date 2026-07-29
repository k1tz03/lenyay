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
# Appels /stats par IP et par minute (le dashboard poll ~15/min).
STATS_RATE_LIMIT = int(_env("STATS_RATE_LIMIT", "60"))
# Preuve de travail : /results exige le bail signé émis par /work.
REQUIRE_LEASE = _env("REQUIRE_LEASE", "1") == "1"
# Durée de vie d'un bail (l'inférence CPU d'un lot peut être longue).
LEASE_TTL = int(_env("LEASE_TTL", "7200"))  # 2 h
# Traces retenues par tâche À L'EXPORT (la sélection se fait hors ligne, avec
# tout le corpus en main : plus de créneau pris définitivement au vol).
ARCHIVE_MAX_PER_TASK = int(_env("ARCHIVE_MAX_PER_TASK", "3"))
# Soumissions par appareil et par jour, ACCEPTÉES OU NON : sans ça, un client
# qui soumet exprès des réponses fausses écrit sans limite sur le disque.
DAILY_SUBMISSION_CAP = int(_env("DAILY_SUBMISSION_CAP", "6000"))
# Tentatives comptées par le serveur pour un couple (appareil, tâche).
MAX_ATTEMPTS_PER_TASK = int(_env("MAX_ATTEMPTS_PER_TASK", "8"))
# Appareils distincts en échec avant qu'une tâche soit déclarée « dure ».
HARD_MIN_DEVICES = int(_env("HARD_MIN_DEVICES", "2"))

# --- Paliers de modèles ----------------------------------------------------
# Un palier = un modèle, un prix, une récompense. Une machine déclare celui
# qu'elle sait servir ; le coordinateur n'envoie une question qu'aux machines
# du bon palier. Servir un gros modèle demande plus de mémoire, donc rapporte
# davantage.
TIERS = {
    "rapide": {
        "id": "rapide",
        "label": "Rapide",
        "model": "Qwen2.5 1.5B",
        "about": "Questions courantes, réponses en quelques secondes.",
        "cost": 1,
        "reward": 3,
    },
    "costaud": {
        "id": "costaud",
        "label": "Costaud",
        "model": "Qwen2.5 7B",
        "about": "Raisonnements longs, rédaction. Plus lent, plus cher.",
        "cost": 5,
        "reward": 12,
    },
    # Le module Code : un modèle spécialisé, et le poste de calcul le plus
    # lourd — donc le palier le plus cher, côté crédits comme, demain, côté
    # abonnement. C'est lui que financent « les personnes qui font du code ».
    "code": {
        "id": "code",
        "label": "Code",
        "model": "Qwen2.5-Coder 7B",
        "about": "Écrire, corriger et expliquer du code. Le palier le plus cher.",
        "cost": 12,
        "reward": 25,
    },
    # Le pas suivant vers le « très grand modèle » : servi en entier par une
    # machine qui en est capable (~12 Go de mémoire libre).
    "geant": {
        "id": "geant",
        "label": "Géant",
        "model": "Qwen2.5 14B",
        "about": "Le plus grand modèle du réseau. Réservé aux machines solides.",
        "cost": 20,
        "reward": 45,
    },
}
# Le modèle GGUF associé à chaque palier : une machine « costaud » télécharge
# le 7B (≈ 4,7 Go, il lui faut ~8 Go de mémoire libre).
TIER_MODELS = {
    "rapide": ("Qwen/Qwen2.5-1.5B-Instruct-GGUF", "q4_k_m"),
    "costaud": ("Qwen/Qwen2.5-7B-Instruct-GGUF", "q4_k_m"),
    "code": ("Qwen/Qwen2.5-Coder-7B-Instruct-GGUF", "q4_k_m"),
    "geant": ("Qwen/Qwen2.5-14B-Instruct-GGUF", "q4_k_m"),
}
# Une machine est « en ligne » pour un palier si elle a donné signe de vie
# dans cette fenêtre (minutes) — sert à n'afficher que les modèles servables.
TIER_ONLINE_WINDOW = int(_env("TIER_ONLINE_WINDOW", "10"))
DEFAULT_TIER = _env("DEFAULT_TIER", "rapide")
# Le palier que cette machine sait servir (côté worker).
WORKER_TIER = _env("TIER", "rapide")
# Messages du fil transmis à la machine comme mémoire de la conversation.
CONTEXT_MESSAGES = int(_env("CONTEXT_MESSAGES", "8"))

# Tentatives de connexion par IP et par quart d'heure.
LOGIN_LIMIT = int(_env("LOGIN_LIMIT", "10"))

# Jeton d'administration. Vide = administration désactivée : impossible de la
# laisser ouverte par oubli, il faut choisir un secret pour l'activer.
ADMIN_TOKEN = _env("ADMIN_TOKEN", "")

# --- Économie ---------------------------------------------------------------
# Le plancher quotidien : une fois par jour, un solde plus bas remonte à ce
# niveau. Le curieux peut toujours poser quelques questions simples ; l'usage
# intensif, lui, se gagne (en contribuant) ou s'achètera (abonnement).
DAILY_FREE_CREDITS = int(_env("DAILY_FREE_CREDITS", "5"))

# --- Comptes et questions --------------------------------------------------
# Crédits offerts à l'ouverture d'un compte : de quoi essayer l'IA sans rien
# donner d'abord — c'est la promesse « gratuite » tenue dès la première minute.
WELCOME_CREDITS = int(_env("WELCOME_CREDITS", "20"))
# Ce que coûte une question servie par le réseau.
QUESTION_COST = int(_env("QUESTION_COST", "3"))
# Ce que rapporte le fait d'y répondre (plus qu'un calcul : c'est du temps réel).
SERVE_REWARD = int(_env("SERVE_REWARD", "5"))
# Longueur maximale d'une question.
QUESTION_MAX_CHARS = int(_env("QUESTION_MAX_CHARS", "2000"))
# Calculs vérifiés exigés avant de pouvoir servir des questions : on ne confie
# pas la parole du réseau à une machine dont on ne sait rien.
SERVE_MIN_ACCEPTED = int(_env("SERVE_MIN_ACCEPTED", "20"))
# Au-delà, une question décrochée mais sans réponse retourne à la file.
SERVE_TIMEOUT = int(_env("SERVE_TIMEOUT", "180"))

# --- Tâches de code ---------------------------------------------------------
# Catalogue des tâches vérifiées par tests unitaires (absent = maths seules).
CODE_TASKS_FILE = Path(_env("CODE_TASKS", str(REPO_ROOT / "data" / "code_tasks.jsonl")))
# Délai d'exécution d'une solution, en secondes.
CODE_TIMEOUT = int(_env("CODE_TIMEOUT", "10"))
# Taille maximale du code extrait.
CODE_MAX_CHARS = int(_env("CODE_MAX_CHARS", "20000"))

# --- Inférence -------------------------------------------------------------
TEMPERATURE = float(_env("TEMPERATURE", "0.8"))
MAX_TOKENS = int(_env("MAX_TOKENS", "640"))
MODEL_REPO = _env("MODEL_REPO", "Qwen/Qwen2.5-1.5B-Instruct-GGUF")
# On sélectionne le fichier GGUF du repo dont le nom contient ce motif.
MODEL_FILE_PATTERN = _env("MODEL_PATTERN", "q4_k_m")
