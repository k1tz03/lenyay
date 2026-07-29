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
    # "math" (réponse exacte) ou "code" (tests unitaires au vert).
    kind: str = "math"


class TaskWithAnswer(Task):
    """Version coordinateur uniquement — ne sort jamais de l'API.

    La réponse attendue (maths) et les tests (code) sont les deux formes du
    même secret : ce qui permet de vérifier sans faire confiance.
    """

    expected_answer: str = ""
    tests: str = ""


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


# Regex volontairement simple : le vrai test d'un e-mail, c'est de s'en servir.
_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class AuthRegisterRequest(BaseModel):
    email: str = Field(pattern=_EMAIL, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    handle: str = Field(default="anonyme", max_length=40)
    # Aider à améliorer Lenyay avec ses conversations (facultatif, désactivé
    # par défaut).
    learn_opt_in: bool = False


class ConsentRequest(BaseModel):
    opt_in: bool


class FeedbackRequest(BaseModel):
    rating: str = Field(pattern=r"^(up|down)$")


class AuthLoginRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


class PasswordChangeRequest(BaseModel):
    current: str = Field(max_length=128)
    new: str = Field(min_length=8, max_length=128)


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
    email: str | None = None
    # La clé n'identifie plus une personne : elle sert à rattacher des machines.
    account_key: str = ""
    learn_opt_in: bool = False


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
    # L'id du message IA, pour pouvoir le noter (👍/👎).
    message_id: int | None = None


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


class RegenerateRequest(BaseModel):
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
