"""Chargement en mémoire du jeu de tâches figé (data/tasks.jsonl).

200 tâches → un dict en mémoire suffit largement ; le fichier JSONL commité
reste la source de vérité.
"""

import json
import random

from common import config
from common.schemas import TaskWithAnswer

_tasks: dict[str, TaskWithAnswer] = {}


def load_tasks() -> int:
    _tasks.clear()
    with config.TASKS_FILE.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                task = TaskWithAnswer(**json.loads(line))
                _tasks[task.task_id] = task
    return len(_tasks)


def get(task_id: str) -> TaskWithAnswer | None:
    return _tasks.get(task_id)


def count() -> int:
    return len(_tasks)


def sample(n: int, exclude: set[str]) -> list[TaskWithAnswer]:
    """n tâches au hasard, en évitant celles déjà résolues par l'appareil.

    Si l'appareil a tout résolu, on repioche dans l'ensemble complet plutôt
    que de le laisser sans travail.
    """
    pool = [t for tid, t in _tasks.items() if tid not in exclude]
    if not pool:
        pool = list(_tasks.values())
    return random.sample(pool, min(n, len(pool)))
