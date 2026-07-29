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
    # Lier l'appareil à un compte : ses gains alimentent alors la bourse.
    account_key: str | None = Field(default=None, max_length=128)
    # Le palier de modèle que cette machine sait servir.
    tier: str = Field(default="rapide", max_length=24)


class RegisterResponse(BaseModel):
    device_id: str
    api_key: str


# --- Soumission de résultats ----------------------------------------------


class ResultSubmission(BaseModel):
    task_id: str = Field(max_length=128)
    # 8 k : une trace GSM8K fait 1-2 k ; au-delà c'est du remplissage.
    trace: str = Field(max_length=8_000)
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


# --- Comptes et questions ---------------------------------------------------


class AccountRequest(BaseModel):
    handle: str = Field(default="anonyme", max_length=40)


class AccountResponse(BaseModel):
    account_id: str
    account_key: str
    handle: str
    credits: int


class AccountState(BaseModel):
    handle: str
    credits: int
    devices: list[dict]
    questions: list[dict]


class AskRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)


class AskResponse(BaseModel):
    question_id: str
    status: str
    cost: int
    credits_left: int


class QuestionState(BaseModel):
    id: str
    status: str
    prompt: str
    answer: str | None = None
    device_name: str | None = None


class ServedQuestion(BaseModel):
    id: str
    prompt: str
    tier: str = "rapide"
    # La mémoire du fil : les échanges précédents, pour que la machine
    # réponde en connaissance de cause.
    context: list[dict] = Field(default_factory=list)


class MessageRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    tier: str = Field(default="rapide", max_length=24)


class Conversation(BaseModel):
    id: str
    title: str
    updated_at: str


class ConversationList(BaseModel):
    conversations: list[Conversation]


class ConversationThread(BaseModel):
    id: str
    title: str
    messages: list[dict]


class ServeOffer(BaseModel):
    question: ServedQuestion | None = None


class AnswerSubmission(BaseModel):
    answer: str = Field(min_length=1, max_length=8000)


class Stats(BaseModel):
    devices_seen: int
    total_rollouts: int
    accepted_rollouts: int
    acceptance_rate: float
    total_credits: int
    tasks_in_catalog: int
    top_contributors: list[ContributorStat]
