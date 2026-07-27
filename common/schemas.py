"""Schémas partagés entre le coordinateur et le worker.

Règle de confiance centrale : `Task` (ce que voit le worker) ne contient JAMAIS
la réponse attendue. `TaskWithAnswer` n'existe que côté coordinateur.
"""

from pydantic import BaseModel


# --- Tâches ---------------------------------------------------------------


class Task(BaseModel):
    """Ce que le worker reçoit : le problème, rien d'autre."""

    task_id: str
    prompt: str


class TaskWithAnswer(Task):
    """Version coordinateur uniquement — ne sort jamais de l'API."""

    expected_answer: str


class WorkBatch(BaseModel):
    tasks: list[Task]


# --- Enregistrement des appareils -----------------------------------------


class RegisterRequest(BaseModel):
    device_name: str = "appareil-anonyme"


class RegisterResponse(BaseModel):
    device_id: str
    api_key: str


# --- Soumission de résultats ----------------------------------------------


class ResultSubmission(BaseModel):
    task_id: str
    trace: str
    attempt: int = 1


class ResultsPayload(BaseModel):
    results: list[ResultSubmission]


class Verdict(BaseModel):
    task_id: str
    accepted: bool
    extracted_answer: str | None
    attempt: int = 1


class SubmitResponse(BaseModel):
    verdicts: list[Verdict]
    credits_earned: int
    total_credits: int


# --- Statistiques ----------------------------------------------------------


class ContributorStat(BaseModel):
    device_id: str
    device_name: str
    credits: int


class Stats(BaseModel):
    devices_seen: int
    total_rollouts: int
    accepted_rollouts: int
    acceptance_rate: float
    top_contributors: list[ContributorStat]
