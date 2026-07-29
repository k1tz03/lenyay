"""Coordinateur Lenyay — API FastAPI + mini-dashboard HTML.

Lancement :  python -m coordinator.app
(LENYAY_HOST / LENYAY_PORT pris en compte ; avec la CLI uvicorn, passer
soi-même --host/--port.)
"""

import hmac
import json
import logging
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from common import config
from common.schemas import (  # noqa: F401 — l'API expose ces modèles
    AccountRequest,
    AuthLoginRequest,
    AuthRegisterRequest,
    PasswordChangeRequest,
    AccountResponse,
    AccountState,
    AnswerSubmission,
    AskRequest,
    AskResponse,
    Conversation,
    ConversationList,
    ConversationThread,
    MessageRequest,
    QuestionState,
    ServedQuestion,
    ServeOffer,
)
from common.schemas import (
    RegisterRequest,
    RegisterResponse,
    ResultsPayload,
    Stats,
    SubmitResponse,
    Task,
    Verdict,
    WorkBatch,
)
from coordinator import auth, codeverify, db, leases, limits, tasks
from coordinator.about import ABOUT_HTML
from coordinator.adminpage import ADMIN_HTML
from coordinator.landing import LANDING_HTML
from coordinator.verifier import verify

logger = logging.getLogger("lenyay.coordinator")
_archive_lock = threading.Lock()
# Un verrou par appareil : les routes sont synchrones, donc exécutées dans un
# pool de threads — sans lui, deux soumissions concurrentes du même appareil
# liraient le même compteur de crédits et franchiraient le plafond.
_device_locks: dict[str, threading.Lock] = {}
_device_locks_guard = threading.Lock()
_MAX_TRACKED_LOCKS = 5_000

# Résultat de hard_task_ids() mis en cache : la requête agrège toute la table
# et le jeu des tâches dures n'évolue que lentement.
_hard_cache: dict[str, object] = {"at": 0.0, "value": set()}
_HARD_TTL = 60.0


def _lock_for(device_id: str) -> threading.Lock:
    with _device_locks_guard:
        if len(_device_locks) > _MAX_TRACKED_LOCKS:
            # Un essaim de faux appareils ne doit pas faire enfler la table
            # des verrous indéfiniment ; les verrous libres sont jetables.
            for key, lock in list(_device_locks.items()):
                if not lock.locked():
                    del _device_locks[key]
        return _device_locks.setdefault(device_id, threading.Lock())


def _hard_tasks() -> set[str]:
    now = time.monotonic()
    if now - float(_hard_cache["at"]) > _HARD_TTL:
        _hard_cache["value"] = db.hard_task_ids()
        _hard_cache["at"] = now
    return _hard_cache["value"]  # type: ignore[return-value]


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    db.init_db()
    n = tasks.load_tasks()
    config.ACCEPTED_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Coordinateur prêt : %d tâches chargées, base %s", n, config.DB_PATH)
    yield


app = FastAPI(title="Lenyay — coordinateur", lifespan=lifespan)

# Polices de la page publique, servies avec le site : aucun appel à un CDN
# tiers, la page ne fait fuiter aucune visite.
_STATIC = Path(__file__).resolve().parent / "static"
_STATIC.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=_STATIC), name="static")


def require_device(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="En-tête X-API-Key manquant")
    device = db.device_for_key(x_api_key)
    if device is None:
        raise HTTPException(status_code=401, detail="Clé API inconnue")
    if not limits.device_limiter.allow(x_api_key, config.RATE_LIMIT, 60.0):
        raise HTTPException(status_code=429, detail="Trop de requêtes — ralentis un peu")
    return device


def _archive_accepted(
    device_id: str, task, trace: str, extracted: str, attempt: int = 1
) -> None:
    """Les traces correctes sont le futur dataset de fine-tuning : JSONL append-only.

    Le numéro de tentative permet de sur-pondérer à l'entraînement les traces
    « durement gagnées » (tentative ≥ 2), les plus instructives."""
    record = {
        "task_id": task.task_id,
        "prompt": task.prompt,
        "expected_answer": task.expected_answer,
        "trace": trace,
        "extracted_answer": extracted,
        "device_id": device_id,
        "attempt": attempt,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = config.ACCEPTED_DIR / f"accepted-{day}.jsonl"
    with _archive_lock:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# --- API -------------------------------------------------------------------


_SESSION_COOKIE = "lenyay_session"


def require_account(request: Request,
                    x_account_key: str | None = Header(default=None, alias="X-Account-Key")):
    """Deux portes : la session (navigateur) ou la clé (machines et scripts).
    La clé n'est plus l'identité d'une personne — c'est un jeton d'API."""
    account = None
    if x_account_key:
        account = db.account_for_key(x_account_key)
        if account is None:
            raise HTTPException(status_code=401, detail="Compte inconnu")
    else:
        token = request.cookies.get(_SESSION_COOKIE)
        if token:
            account = db.account_for_session(token)
    if account is None:
        raise HTTPException(status_code=401, detail="Connexion requise")
    if "banned" in account.keys() and account["banned"]:
        raise HTTPException(status_code=403, detail="Compte suspendu")
    return account


def require_admin(x_admin_token: str | None = Header(default=None, alias="X-Admin-Token")):
    """L'administration n'existe que si un secret a été choisi (LENYAY_ADMIN_TOKEN)."""
    if not config.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Administration désactivée")
    if not x_admin_token or not hmac.compare_digest(x_admin_token, config.ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Jeton d'administration invalide")
    return True


@app.post("/devices/register", response_model=RegisterResponse)
def register(payload: RegisterRequest, request: Request):
    client_ip = request.client.host if request.client else "inconnue"
    if not limits.register_limiter.allow(client_ip, config.REGISTER_LIMIT, 3600.0):
        raise HTTPException(
            status_code=429,
            detail="Trop d'enregistrements depuis cette adresse — réessaie plus tard",
        )
    account_id = None
    if payload.account_key:
        account = db.account_for_key(payload.account_key)
        if account is None:
            raise HTTPException(status_code=401, detail="Clé de compte inconnue")
        account_id = account["account_id"]
    tier = payload.tier if payload.tier in config.TIERS else config.DEFAULT_TIER
    device_id, api_key = db.register_device(payload.device_name, account_id, tier)
    logger.info("Nouvel appareil enregistré : %s (%s)", payload.device_name, device_id[:8])
    return RegisterResponse(device_id=device_id, api_key=api_key)


@app.get("/work", response_model=WorkBatch)
def get_work(
    n: int = Query(default=config.BATCH_SIZE, ge=1, le=32),
    device=Depends(require_device),
):
    device_id = device["device_id"]
    solved = db.accepted_task_ids(device_id)
    hard = _hard_tasks() if config.HUNT_MODE else None
    batch = tasks.sample(n, exclude=solved, hard_first=hard)
    secret = db.server_secret()
    # Task (sans expected_answer) : la réponse attendue ne sort JAMAIS d'ici.
    # Chaque tâche part avec son bail signé, à renvoyer avec le résultat.
    return WorkBatch(tasks=[
        Task(
            task_id=t.task_id,
            prompt=t.prompt,
            kind=t.kind,
            lease=leases.issue(secret, device_id, t.task_id, config.LEASE_TTL),
        )
        for t in batch
    ])


@app.post("/results", response_model=SubmitResponse)
def submit_results(payload: ResultsPayload, device=Depends(require_device)):
    device_id = device["device_id"]
    with _lock_for(device_id):
        return _submit_locked(payload, device, device_id)


def _submit_locked(payload: ResultsPayload, device, device_id: str) -> SubmitResponse:
    # Une tâche déjà acceptée par cet appareil ne rapporte plus rien : pas de
    # nouveau crédit, pas de doublon dans le dataset (le rollout reste journalisé).
    already_accepted = db.accepted_task_ids(device_id)
    credited_today = db.accepted_today(device_id)
    submitted_today = db.submissions_today(device_id)
    if config.DAILY_CREDIT_CAP and credited_today >= config.DAILY_CREDIT_CAP:
        # Plafond atteint : on refuse AVANT de consommer les tâches, sinon
        # elles seraient marquées résolues sans jamais être créditées.
        raise HTTPException(
            status_code=429,
            detail="Quota quotidien atteint — reprends demain (réinitialisation à 00:00 UTC)",
        )
    if config.DAILY_SUBMISSION_CAP and submitted_today >= config.DAILY_SUBMISSION_CAP:
        # Compte TOUTES les soumissions : sans ça, enchaîner des réponses
        # fausses permet d'écrire sans fin sur le disque du serveur.
        raise HTTPException(
            status_code=429,
            detail="Trop de soumissions aujourd'hui — reprends demain (00:00 UTC)",
        )
    secret = db.server_secret()
    verdicts: list[Verdict] = []
    earned = 0
    written = 0
    for result in payload.results:
        task = tasks.get(result.task_id)
        if task is None:
            verdicts.append(
                Verdict(task_id=result.task_id, accepted=False,
                        extracted_answer=None, attempt=0)
            )
            continue
        if config.REQUIRE_LEASE and not leases.verify(
            secret, device_id, result.task_id, result.lease
        ):
            # Preuve de travail manquante : la tâche n'a pas été distribuée à
            # cet appareil. Rien n'est journalisé, rien n'est crédité.
            logger.info("Bail invalide : %s sur %s", device["device_name"], result.task_id)
            verdicts.append(
                Verdict(task_id=result.task_id, accepted=False,
                        extracted_answer=None, attempt=0)
            )
            continue
        # Le numéro de tentative est COMPTÉ par le serveur : il sert de
        # pondération à l'entraînement, il ne peut pas venir du client.
        attempt = db.attempts_for_task(device_id, result.task_id) + 1
        if attempt > config.MAX_ATTEMPTS_PER_TASK:
            # Un bail reste valide plusieurs heures : sans ce compteur, il
            # serait rejouable en boucle pour remplir la base.
            verdicts.append(
                Verdict(task_id=result.task_id, accepted=False,
                        extracted_answer=None, attempt=attempt - 1)
            )
            continue
        if config.DAILY_SUBMISSION_CAP and submitted_today + written >= config.DAILY_SUBMISSION_CAP:
            verdicts.append(
                Verdict(task_id=result.task_id, accepted=False,
                        extracted_answer=None, attempt=attempt - 1)
            )
            continue
        if task.kind == "code":
            # Le juge est un jeu de tests, pas un nombre — même principe :
            # vérifiable, binaire, et le secret (les tests) reste au serveur.
            accepted, extracted = codeverify.verify_code(result.trace, task.tests)
        else:
            accepted, extracted = verify(result.trace, task.expected_answer)
        if accepted and len(result.trace.strip()) < config.MIN_TRACE_CHARS:
            # Bonne réponse sans raisonnement : aucune valeur pour le dataset,
            # et signature classique d'une réponse copiée. Pas de crédit.
            accepted = False
            logger.info("Trace creuse refusée : %s sur %s",
                        device["device_name"], result.task_id)
        db.record_rollout(
            device_id, result.task_id, attempt, result.trace, extracted, accepted
        )
        written += 1
        if accepted and result.task_id not in already_accepted:
            earned += 1
            already_accepted.add(result.task_id)
            # Toutes les traces correctes sont versées au corpus brut ; le
            # tri (quota par tâche, diversité) se fait à l'export, avec tout
            # le corpus en main — arriver le premier ne donne aucun droit.
            _archive_accepted(device_id, task, result.trace, extracted, attempt)
            if config.DAILY_CREDIT_CAP and credited_today + earned >= config.DAILY_CREDIT_CAP:
                logger.info("Plafond quotidien atteint pour %s", device["device_name"])
        verdicts.append(
            Verdict(task_id=result.task_id, accepted=accepted,
                    extracted_answer=extracted, attempt=attempt)
        )
    total = db.add_credits(device_id, earned)
    logger.info(
        "Résultats de %s : %d soumis, %d acceptés (total crédits : %d)",
        device["device_name"], len(payload.results), earned, total,
    )
    return SubmitResponse(verdicts=verdicts, credits_earned=earned, total_credits=total)


# --- Authentification -------------------------------------------------------


def _open_session(response, account_id: str) -> None:
    token = auth.new_session_token()
    db.create_session(account_id, token)
    response.set_cookie(
        _SESSION_COOKIE, token, httponly=True, samesite="lax",
        max_age=30 * 24 * 3600, path="/",
    )


@app.post("/auth/register", response_model=AccountResponse)
def auth_register(payload: AuthRegisterRequest, request: Request, response: Response):
    client_ip = request.client.host if request.client else "inconnue"
    if not limits.register_limiter.allow(f"acct:{client_ip}", config.REGISTER_LIMIT, 3600.0):
        raise HTTPException(status_code=429, detail="Trop de comptes créés depuis cette adresse")
    handle = payload.handle.strip() or "anonyme"
    created = db.create_user_account(
        handle, payload.email.strip().lower(),
        auth.hash_password(payload.password), config.WELCOME_CREDITS,
    )
    if created is None:
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cet e-mail")
    account_id, api_key = created
    _open_session(response, account_id)
    logger.info("Nouveau compte : %s (%s…)", handle, account_id[:8])
    return AccountResponse(account_id=account_id, account_key=api_key,
                           handle=handle, credits=config.WELCOME_CREDITS)


@app.post("/auth/login", response_model=AccountResponse)
def auth_login(payload: AuthLoginRequest, request: Request, response: Response):
    client_ip = request.client.host if request.client else "inconnue"
    if not limits.register_limiter.allow(f"login:{client_ip}", config.LOGIN_LIMIT, 900.0):
        raise HTTPException(status_code=429, detail="Trop de tentatives — réessaie plus tard")
    account = db.account_for_email(payload.email.strip().lower())
    # Toujours la même réponse, que l'e-mail existe ou non : on ne donne pas
    # la liste de nos membres à qui essaie des adresses.
    if account is None or not auth.verify_password(
            payload.password, account["password_hash"] or ""):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    _open_session(response, account["account_id"])
    return AccountResponse(account_id=account["account_id"], account_key=account["api_key"],
                           handle=account["handle"], credits=account["credits"])


@app.post("/auth/logout")
def auth_logout(request: Request, response: Response):
    token = request.cookies.get(_SESSION_COOKIE)
    if token:
        db.delete_session(token)
    response.delete_cookie(_SESSION_COOKIE, path="/")
    return {"logged_out": True}


@app.post("/auth/password")
def auth_change_password(payload: PasswordChangeRequest, account=Depends(require_account)):
    if not auth.verify_password(payload.current, account["password_hash"] or ""):
        raise HTTPException(status_code=401, detail="Mot de passe actuel incorrect")
    db.set_password(account["account_id"], auth.hash_password(payload.new))
    return {"changed": True}


# --- Administration ---------------------------------------------------------


@app.get("/admin/members")
def admin_members(_=Depends(require_admin)):
    return {"members": db.admin_members()}


@app.post("/admin/members/{account_id}/credits")
def admin_adjust_credits(account_id: str, payload: dict, _=Depends(require_admin)):
    amount = int(payload.get("amount", 0))
    reason = str(payload.get("reason", "")).strip() or "Ajustement administrateur"
    if amount == 0 or abs(amount) > 100_000:
        raise HTTPException(status_code=422, detail="Montant invalide")
    balance = db.move_account_credits(account_id, amount, kind="adjust",
                                      label=f"Ajustement — {reason}")
    logger.info("Admin : %+d crédits pour %s… (%s)", amount, account_id[:8], reason)
    return {"credits": balance}


@app.post("/admin/members/{account_id}/ban")
def admin_ban(account_id: str, payload: dict, _=Depends(require_admin)):
    banned = bool(payload.get("banned", True))
    if not db.set_account_ban(account_id, banned):
        raise HTTPException(status_code=404, detail="Membre inconnu")
    logger.info("Admin : compte %s… %s", account_id[:8],
                "suspendu" if banned else "rétabli")
    return {"banned": banned}


@app.get("/admin/overview")
def admin_overview(_=Depends(require_admin)):
    members = db.admin_members()
    return {
        "members": len(members),
        "banned": sum(1 for m in members if m["banned"]),
        "questions": db.questions_overview(),
        "stats": {**db.stats(), "tasks_in_catalog": tasks.count()},
    }


# --- Comptes ---------------------------------------------------------------


@app.post("/accounts", response_model=AccountResponse)
def create_account(payload: AccountRequest, request: Request):
    client_ip = request.client.host if request.client else "inconnue"
    if not limits.register_limiter.allow(f"acct:{client_ip}", config.REGISTER_LIMIT, 3600.0):
        raise HTTPException(status_code=429, detail="Trop de comptes créés depuis cette adresse")
    handle = payload.handle.strip() or "anonyme"
    account_id, account_key = db.create_account(handle, config.WELCOME_CREDITS)
    logger.info("Nouveau compte : %s (%s…)", handle, account_id[:8])
    return AccountResponse(account_id=account_id, account_key=account_key,
                           handle=handle, credits=config.WELCOME_CREDITS)


@app.get("/accounts/ledger")
def account_ledger(account=Depends(require_account)):
    """Le relevé du compte : d'où viennent les crédits, où ils sont partis."""
    account_id = account["account_id"]
    return {"entries": db.ledger_entries(account_id),
            "summary": db.ledger_summary(account_id)}


@app.get("/accounts/me", response_model=AccountState)
def account_state(account=Depends(require_account)):
    # Le passage quotidien : si le solde est sous le plancher, il y remonte.
    db.apply_daily_refill(account["account_id"], config.DAILY_FREE_CREDITS)
    account = db.account_for_key(account["api_key"])
    keys = account.keys()
    return AccountState(
        handle=account["handle"],
        credits=account["credits"],
        devices=db.account_devices(account["account_id"]),
        questions=db.recent_questions(account["account_id"]),
        email=account["email"] if "email" in keys else None,
        account_key=account["api_key"],
    )


# --- Paliers de modèles -----------------------------------------------------


@app.get("/tiers")
def tiers():
    """Les modèles proposés, leur prix, et combien de machines peuvent les
    servir en ce moment — le chat n'affiche pas de promesse sans machine."""
    online = db.online_devices_by_tier(config.TIER_ONLINE_WINDOW)
    return {
        "tiers": [{**t, "online": online.get(t["id"], 0)}
                  for t in config.TIERS.values()],
        "default": config.DEFAULT_TIER,
    }


# --- Conversations ----------------------------------------------------------


def _owned_conversation(conversation_id: str, account):
    conv = db.get_conversation(conversation_id, account["account_id"])
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    return conv


@app.post("/conversations", response_model=Conversation)
def new_conversation(account=Depends(require_account)):
    conv = db.create_conversation(account["account_id"])
    return Conversation(**conv)


@app.get("/conversations", response_model=ConversationList)
def conversations(account=Depends(require_account)):
    return ConversationList(
        conversations=[Conversation(**c) for c in db.list_conversations(account["account_id"])]
    )


@app.get("/conversations/{conversation_id}", response_model=ConversationThread)
def conversation_thread(conversation_id: str, account=Depends(require_account)):
    conv = _owned_conversation(conversation_id, account)
    return ConversationThread(id=conv["id"], title=conv["title"],
                              messages=db.conversation_messages(conversation_id))


@app.delete("/conversations/{conversation_id}")
def remove_conversation(conversation_id: str, account=Depends(require_account)):
    if not db.delete_conversation(conversation_id, account["account_id"]):
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    return {"deleted": conversation_id}


def _charge_and_queue(account, prompt: str, tier_id: str,
                      conversation_id: str | None) -> AskResponse:
    """Débite le compte au tarif du palier, puis met la question en file."""
    account_id = account["account_id"]
    if not limits.device_limiter.allow(f"ask:{account_id}", config.RATE_LIMIT, 60.0):
        raise HTTPException(status_code=429, detail="Trop de questions à la suite")
    tier = config.TIERS.get(tier_id) or config.TIERS[config.DEFAULT_TIER]
    db.apply_daily_refill(account_id, config.DAILY_FREE_CREDITS)
    if not db.spend_credits(account_id, tier["cost"],
                            label=f"Question — modèle {tier['label'].lower()}"):
        raise HTTPException(
            status_code=402,
            detail=(
                f"Crédits insuffisants : « {tier['label']} » en coûte {tier['cost']}. "
                "Deux façons d'en avoir : contribuer en laissant Lenyay tourner sur ta "
                "machine, ou prendre un abonnement (bientôt disponible)."
            ),
        )
    question_id = db.create_question(account_id, prompt, tier["cost"],
                                     conversation_id, tier["id"])
    remaining = db.account_for_key(account["api_key"])["credits"]
    logger.info("Question %s (%s) posée par %s", question_id, tier["id"], account["handle"])
    return AskResponse(question_id=question_id, status="pending",
                       cost=tier["cost"], credits_left=remaining)


@app.post("/conversations/{conversation_id}/messages", response_model=AskResponse)
def post_message(conversation_id: str, payload: MessageRequest,
                 account=Depends(require_account)):
    """Un message dans un fil : la mémoire de la conversation part avec lui."""
    conv = _owned_conversation(conversation_id, account)
    prompt = payload.prompt.strip()
    response = _charge_and_queue(account, prompt, payload.tier, conversation_id)
    db.add_message(conversation_id, "user", prompt, tier=payload.tier)
    if conv["title"] == "Nouvelle conversation":
        # Le titre du fil vient de sa première phrase, comme partout ailleurs.
        title = prompt[:60] + ("…" if len(prompt) > 60 else "")
        db.set_conversation_title(conversation_id, title)
    return response


# --- Poser une question au réseau (sans fil) --------------------------------


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, account=Depends(require_account)):
    """Le chaînon : une question part sur le réseau et sera traitée par la
    machine d'un autre membre, payée en crédits."""
    return _charge_and_queue(account, payload.prompt.strip(), config.DEFAULT_TIER, None)


@app.get("/ask/{question_id}", response_model=QuestionState)
def question_state(question_id: str):
    """Suivi public d'une question : son identifiant fait office de jeton."""
    db.release_stale_questions(config.SERVE_TIMEOUT)
    row = db.get_question(question_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Question inconnue")
    return QuestionState(id=row["id"], status=row["status"], prompt=row["prompt"],
                         answer=row["answer"], device_name=row["device_name"])


# --- Servir une question (côté machine) ------------------------------------


@app.get("/serve", response_model=ServeOffer)
def serve(device=Depends(require_device)):
    """Une machine éprouvée vient chercher une question à traiter."""
    device_id = device["device_id"]
    if db.accepted_count(device_id) < config.SERVE_MIN_ACCEPTED:
        # On ne confie pas la parole du réseau à une machine sans historique.
        return ServeOffer(question=None)
    db.release_stale_questions(config.SERVE_TIMEOUT)
    tier = device["tier"] if "tier" in device.keys() and device["tier"] else config.DEFAULT_TIER
    row = db.claim_question(device_id, device["device_name"], tier)
    if row is None:
        return ServeOffer(question=None)
    # La mémoire du fil accompagne la question : la machine répond en
    # connaissant les échanges précédents, comme un vrai assistant.
    context: list[dict] = []
    if row["conversation_id"]:
        history = db.conversation_messages(row["conversation_id"], config.CONTEXT_MESSAGES)
        context = [{"role": m["role"], "content": m["content"]}
                   for m in history if m["content"] != row["prompt"]]
    logger.info("Question %s (%s) confiée à %s", row["id"], tier, device["device_name"])
    return ServeOffer(question=ServedQuestion(
        id=row["id"], prompt=row["prompt"], tier=row["tier"], context=context))


@app.post("/serve/{question_id}")
def submit_answer(question_id: str, payload: AnswerSubmission,
                  device=Depends(require_device)):
    row = db.get_question(question_id)
    answer = payload.answer.strip()
    if not db.answer_question(question_id, device["device_id"], answer):
        raise HTTPException(
            status_code=409,
            detail="Cette question ne t'a pas été confiée, ou a déjà été traitée.",
        )
    if row is not None and row["conversation_id"]:
        db.add_message(row["conversation_id"], "assistant", answer,
                       device_name=device["device_name"], tier=row["tier"])
    tier = config.TIERS.get(row["tier"] if row else config.DEFAULT_TIER,
                            config.TIERS[config.DEFAULT_TIER])
    reward = tier["reward"]
    total = db.add_credits(device["device_id"], reward, kind="served",
                           label=f"Réponse servie — modèle {tier['label'].lower()}")
    logger.info("Question %s traitée par %s (+%d crédits)",
                question_id, device["device_name"], reward)
    return {"earned": reward, "total_credits": total}


@app.get("/stats", response_model=Stats)
def get_stats(request: Request):
    # Endpoint public (le dashboard le poll), donc borné par IP contre
    # l'amplification : chaque appel agrège toute la table rollouts.
    client_ip = request.client.host if request.client else "inconnue"
    if not limits.public_limiter.allow(client_ip, config.STATS_RATE_LIMIT, 60.0):
        raise HTTPException(status_code=429, detail="Trop de requêtes /stats")
    return Stats(**db.stats(), tasks_in_catalog=tasks.count())


# --- Dashboard -------------------------------------------------------------
# Page statique unique : les compteurs sont alimentés en direct par un fetch
# de /stats toutes les 4 s (pas de rechargement complet, pas de framework).
# Les noms d'appareils sont injectés via textContent → pas de XSS possible.

_PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lenyay — coordinateur</title>
<style>
  :root{
    --bg:#0f1413; --panel:#161d1b; --border:#243030;
    --text:#e6edea; --muted:#87999a;
    --accent:#72b5a3; --accent-soft:rgba(114,181,163,.18); --bad:#c4726f;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);
       font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
       -webkit-font-smoothing:antialiased}
  .wrap{max-width:760px;margin:0 auto;padding:2rem 1.25rem 3rem}
  header{display:flex;align-items:baseline;gap:.75rem;flex-wrap:wrap;
         margin-bottom:1.75rem}
  h1{font-size:1.5rem;margin:0;letter-spacing:.02em}
  h1 small{color:var(--muted);font-weight:400;font-size:.95rem}
  #live{margin-left:auto;display:flex;align-items:center;gap:.45rem;
        color:var(--muted);font-size:.8rem}
  #live .dot{width:.55rem;height:.55rem;border-radius:50%;
             background:var(--accent);animation:pulse 2.5s infinite}
  #live.off .dot{background:var(--bad);animation:none}
  @keyframes pulse{0%{box-shadow:0 0 0 0 var(--accent-soft)}
                   70%{box-shadow:0 0 0 .5rem transparent}
                   100%{box-shadow:0 0 0 0 transparent}}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
         gap:.75rem}
  .card{background:var(--panel);border:1px solid var(--border);
        border-radius:10px;padding:1rem 1.1rem}
  .card b{display:block;font-size:1.9rem;font-weight:650;
          font-variant-numeric:tabular-nums;color:var(--accent)}
  .card span{color:var(--muted);font-size:.82rem}
  section h2{font-size:.9rem;color:var(--muted);font-weight:600;
             margin:2rem 0 .75rem;text-transform:uppercase;letter-spacing:.08em}
  table{width:100%;border-collapse:collapse;background:var(--panel);
        border:1px solid var(--border);border-radius:10px;overflow:hidden}
  th,td{text-align:left;padding:.65rem .9rem;border-top:1px solid var(--border);
        font-size:.92rem}
  thead th{border-top:none;color:var(--muted);font-size:.76rem;
           text-transform:uppercase;letter-spacing:.06em}
  td.num{text-align:right;font-variant-numeric:tabular-nums;
         color:var(--accent);font-weight:600}
  td .id{color:var(--muted);font-family:ui-monospace,Consolas,monospace;
         font-size:.78rem}
  td .when{color:var(--muted);font-size:.85rem}
  .on::before{content:"";display:inline-block;width:.45rem;height:.45rem;
              border-radius:50%;background:var(--accent);margin-right:.45rem}
  footer{color:var(--muted);font-size:.78rem;margin-top:1.5rem}
  @media (max-width:480px){
    .wrap{padding:1.25rem .9rem 2rem}
    .card b{font-size:1.5rem}
    th:first-child,td:first-child{display:none}
  }
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>🐝 Lenyay <small>— coordinateur · phase 0</small></h1>
  <div id="live"><span class="dot"></span><span id="live-label">connexion…</span></div>
</header>
<div class="cards">
  <div class="card"><b id="stat-rollouts">–</b><span>rollouts vérifiés</span></div>
  <div class="card"><b id="stat-rate">–</b><span>taux d'acceptation</span></div>
  <div class="card"><b id="stat-credits">–</b><span>crédits distribués</span></div>
  <div class="card"><b id="stat-devices">–</b><span>appareils vus</span></div>
</div>
<section>
<h2>Appareils</h2>
<table>
  <thead><tr><th>#</th><th>Appareil</th><th>Dernière activité</th><th>Crédits</th></tr></thead>
  <tbody id="devices"><tr><td colspan="4">Chargement…</td></tr></tbody>
</table>
</section>
<footer id="footer">–</footer>
</div>
<script>
const $ = id => document.getElementById(id);
const fmt = n => n.toLocaleString("fr-FR");

function ago(iso) {
  const t = Date.parse(iso);
  if (!iso || isNaN(t)) return "—";
  const s = Math.max(0, (Date.now() - t) / 1000);
  if (s < 10) return "à l'instant";
  if (s < 60) return "il y a " + Math.round(s) + " s";
  if (s < 3600) return "il y a " + Math.round(s / 60) + " min";
  if (s < 86400) return "il y a " + Math.round(s / 3600) + " h";
  return "il y a " + Math.round(s / 86400) + " j";
}

function render(s) {
  $("stat-rollouts").textContent = fmt(s.total_rollouts);
  $("stat-rate").textContent =
    (100 * s.acceptance_rate).toFixed(1).replace(".", ",") + " %";
  $("stat-credits").textContent = fmt(s.total_credits);
  $("stat-devices").textContent = fmt(s.devices_seen);
  const tbody = $("devices");
  tbody.replaceChildren();
  if (!s.top_contributors.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 4;
    td.textContent = "Aucun contributeur pour l'instant";
    tr.append(td); tbody.append(tr);
  }
  s.top_contributors.forEach((c, i) => {
    const tr = document.createElement("tr");
    const rank = document.createElement("td");
    rank.textContent = i + 1;
    const name = document.createElement("td");
    const label = document.createElement("span");
    label.textContent = c.device_name;
    const idTag = document.createElement("span");
    idTag.className = "id";
    idTag.textContent = " " + c.device_id.slice(0, 8);
    name.append(label, idTag);
    const when = document.createElement("td");
    const active = (Date.now() - Date.parse(c.last_seen)) / 1000 < 120;
    if (active) when.className = "on";
    const w = document.createElement("span");
    w.className = "when";
    w.textContent = ago(c.last_seen);
    when.append(w);
    const credits = document.createElement("td");
    credits.className = "num";
    credits.textContent = fmt(c.credits);
    tr.append(rank, name, when, credits);
    tbody.append(tr);
  });
  $("footer").textContent = fmt(s.tasks_in_catalog) +
    " tâches GSM8K au catalogue — mise à jour automatique toutes les 4 s";
}

async function tick() {
  try {
    const r = await fetch("/stats", { cache: "no-store" });
    if (!r.ok) throw new Error(r.status);
    render(await r.json());
    $("live").classList.remove("off");
    $("live-label").textContent = "en direct";
  } catch (e) {
    $("live").classList.add("off");
    $("live-label").textContent = "hors ligne";
  }
}
tick();
setInterval(tick, 4000);
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def landing():
    """L'application : le chat, nu. L'explication vit sur /decouvrir."""
    return LANDING_HTML


@app.get("/decouvrir", response_class=HTMLResponse)
def decouvrir():
    """Tout ce qui raconte Lenyay — le cycle jour/nuit, les crédits, l'état réel."""
    return ABOUT_HTML


@app.get("/admin", response_class=HTMLResponse)
def admin_console():
    """La console : une coquille sans secret, le jeton reste chez l'admin."""
    return ADMIN_HTML


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return _PAGE


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("coordinator.app:app", host=config.HOST, port=config.PORT)
