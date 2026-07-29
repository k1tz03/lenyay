"""Schémas partagés entre le coordinateur et le worker.

Règle de confiance centrale : `Task` (ce que voit le worker) ne contient JAMAIS
la réponse attendue. `TaskWithAnswer` n'existe que côté coordinateur.
"""

from pydantic import BaseModel, Field


# --- Tâches ---------------------------------------------------------------


class Task(BaseModel):
    """Ce que le worker reçoit : le problème et son bail, rien d'autre.

    Le bail (HMAC signé par le coordinateur) devra être renvoyé avec le
    résultat : c'est la preuve que la tâche a bien été distribuée.
    """

    task_id: str
    prompt: str
    lease: str = ""


class TaskWithAnswer(Task):
    """Version coordinateur uniquement — ne sort jamais de l'API."""

    expected_answer: str


class WorkBatch(BaseModel):
    tasks: list[Task]


# --- Enregistrement des appareils -----------------------------------------


class RegisterRequest(BaseModel):
    device_name: str = Field(default="appareil-anonyme", max_length=64)


class RegisterResponse(BaseModel):
    device_id: str
    api_key: str


# --- Soumission de résultats ----------------------------------------------


class ResultSubmission(BaseModel):
    task_id: str = Field(max_length=128)
    trace: str = Field(max_length=32_000)
    attempt: int = Field(default=1, ge=1, le=32)
    lease: str = Field(default="", max_length=128)


class ResultsPayload(BaseModel):
    results: list[ResultSubmission] = Field(max_length=64)


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
    last_seen: str = ""  # ISO 8601 — « dernière activité » sur le dashboard


class Stats(BaseModel):
    devices_seen: int
    total_rollouts: int
    accepted_rollouts: int
    acceptance_rate: float
    total_credits: int
    tasks_in_catalog: int
    top_contributors: list[ContributorStat]
