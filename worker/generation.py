"""Générateurs de traces : mock (développement) ou vrai modèle (worker/inference.py).

Le mock simule un LLM avec ~30 % de bonnes réponses. Pour savoir quelle est la
bonne réponse, il triche en lisant data/tasks.jsonl localement — possible en
phase 0 puisque worker et coordinateur tournent sur la même machine. Le vrai
modèle, lui, ne voit jamais la réponse : la frontière de confiance de l'API
reste intacte.
"""

import json
import random

from common import config
from common.schemas import Task


class MockGenerator:
    name = "mock"

    def __init__(self):
        self._answers: dict[str, str] = {}
        try:
            with config.TASKS_FILE.open(encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        self._answers[record["task_id"]] = record["expected_answer"]
        except FileNotFoundError:
            # Sans le fichier local, le mock répond au hasard (≈ 0 % accepté).
            pass

    def generate(self, task: Task) -> str:
        expected = self._answers.get(task.task_id)
        if expected is not None and random.random() < config.MOCK_ACCURACY:
            answer = expected
        else:
            answer = str(random.randint(0, 999))
        return f"(trace simulée) Je réfléchis pas à pas... #### {answer}"

    def answer(self, question: str, context: list[dict] | None = None) -> str:
        suite = f" [{len(context)} message(s) de contexte]" if context else ""
        return f"(réponse simulée à : {question[:60]}){suite}"


def make_generator():
    if config.MOCK_MODE:
        return MockGenerator()
    # Import paresseux : llama-cpp-python n'est requis qu'en mode réel.
    from worker.inference import LlamaGenerator

    return LlamaGenerator()
