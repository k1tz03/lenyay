"""Chargement en mémoire du jeu de tâches figé (data/tasks.jsonl).

200 tâches → un dict en mémoire suffit largement ; le fichier JSONL commité
reste la source de vérité.
"""

import json
import logging
import random

from pydantic import ValidationError

from common import config
from common.schemas import TaskWithAnswer

logger = logging.getLogger("lenyay.coordinator")

_tasks: dict[str, TaskWithAnswer] = {}


def load_tasks() -> int:
    """Charge le catalogue ; une ligne corrompue est ignorée (et journalisée),
    elle ne doit pas empêcher le coordinateur de servir les 199 autres."""
    _tasks.clear()
    if not config.TASKS_FILE.exists():
        raise RuntimeError(
            f"Catalogue introuvable : {config.TASKS_FILE} — lance d'abord "
            "scripts/seed_tasks.py (voir README)."
        )
    skipped = 0
    with config.TASKS_FILE.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                task = TaskWithAnswer(**json.loads(line))
            except (json.JSONDecodeError, ValidationError) as exc:
                logger.warning(
                    "%s ligne %d ignorée (%s)",
                    config.TASKS_FILE.name, lineno, type(exc).__name__,
                )
                skipped += 1
                continue
            _tasks[task.task_id] = task
    if skipped:
        logger.warning("%d ligne(s) corrompue(s) ignorée(s) dans le catalogue", skipped)
    return len(_tasks)


def get(task_id: str) -> TaskWithAnswer | None:
    return _tasks.get(task_id)


def count() -> int:
    return len(_tasks)


def sample(n: int, exclude: set[str]) -> list[TaskWithAnswer]:
    """n tâches au hasard parmi celles que l'appareil n'a pas encore résolues.

    Catalogue épuisé → lot vide : le worker se met en pause plutôt que de
    re-résoudre (et re-créditer) des tâches déjà acceptées.
    """
    pool = [t for tid, t in _tasks.items() if tid not in exclude]
    return random.sample(pool, min(n, len(pool)))
