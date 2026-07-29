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
    catalogs = [config.TASKS_FILE]
    # Le code est le deuxième terrain vérifiable : son catalogue, s'il existe,
    # rejoint la même rotation que les maths.
    if config.CODE_TASKS_FILE.exists():
        catalogs.append(config.CODE_TASKS_FILE)
    for path in catalogs:
        with path.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    task = TaskWithAnswer(**json.loads(line))
                except (json.JSONDecodeError, ValidationError) as exc:
                    logger.warning(
                        "%s ligne %d ignorée (%s)", path.name, lineno,
                        type(exc).__name__,
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


def sample(
    n: int, exclude: set[str], hard_first: set[str] | None = None
) -> list[TaskWithAnswer]:
    """n tâches au hasard parmi celles que l'appareil n'a pas encore résolues.

    En mode chasse (hard_first), les tâches déjà ratées par tout le monde
    passent en tête de lot ; le reste complète. Catalogue épuisé → lot vide.
    """
    pool = [t for tid, t in _tasks.items() if tid not in exclude]
    if hard_first:
        hard = [t for t in pool if t.task_id in hard_first]
        rest = [t for t in pool if t.task_id not in hard_first]
        picked = random.sample(hard, min(n, len(hard)))
        if len(picked) < n:
            picked += random.sample(rest, min(n - len(picked), len(rest)))
        return picked
    return random.sample(pool, min(n, len(pool)))
