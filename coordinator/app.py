"""Coordinateur Essaim — API FastAPI + mini-dashboard HTML.

Lancement :  python -m coordinator.app
(ESSAIM_HOST / ESSAIM_PORT pris en compte ; avec la CLI uvicorn, passer
soi-même --host/--port.)
"""

import html
import json
import logging
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse

from common import config
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
from coordinator import db, tasks
from coordinator.verifier import verify

logger = logging.getLogger("essaim.coordinator")
_archive_lock = threading.Lock()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    db.init_db()
    n = tasks.load_tasks()
    config.ACCEPTED_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Coordinateur prêt : %d tâches chargées, base %s", n, config.DB_PATH)
    yield


app = FastAPI(title="Essaim — coordinateur", lifespan=lifespan)


def require_device(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="En-tête X-API-Key manquant")
    device = db.device_for_key(x_api_key)
    if device is None:
        raise HTTPException(status_code=401, detail="Clé API inconnue")
    return device


def _archive_accepted(device_id: str, task, trace: str, extracted: str) -> None:
    """Les traces correctes sont le futur dataset de fine-tuning : JSONL append-only."""
    record = {
        "task_id": task.task_id,
        "prompt": task.prompt,
        "expected_answer": task.expected_answer,
        "trace": trace,
        "extracted_answer": extracted,
        "device_id": device_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = config.ACCEPTED_DIR / f"accepted-{day}.jsonl"
    with _archive_lock:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# --- API -------------------------------------------------------------------


@app.post("/devices/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
    device_id, api_key = db.register_device(payload.device_name)
    logger.info("Nouvel appareil enregistré : %s (%s)", payload.device_name, device_id[:8])
    return RegisterResponse(device_id=device_id, api_key=api_key)


@app.get("/work", response_model=WorkBatch)
def get_work(
    n: int = Query(default=config.BATCH_SIZE, ge=1, le=32),
    device=Depends(require_device),
):
    solved = db.accepted_task_ids(device["device_id"])
    batch = tasks.sample(n, exclude=solved)
    # Task (sans expected_answer) : la réponse attendue ne sort JAMAIS d'ici.
    return WorkBatch(tasks=[Task(task_id=t.task_id, prompt=t.prompt) for t in batch])


@app.post("/results", response_model=SubmitResponse)
def submit_results(payload: ResultsPayload, device=Depends(require_device)):
    device_id = device["device_id"]
    # Une tâche déjà acceptée par cet appareil ne rapporte plus rien : pas de
    # nouveau crédit, pas de doublon dans le dataset (le rollout reste journalisé).
    already_accepted = db.accepted_task_ids(device_id)
    verdicts: list[Verdict] = []
    earned = 0
    for result in payload.results:
        task = tasks.get(result.task_id)
        if task is None:
            verdicts.append(
                Verdict(task_id=result.task_id, accepted=False,
                        extracted_answer=None, attempt=result.attempt)
            )
            continue
        accepted, extracted = verify(result.trace, task.expected_answer)
        db.record_rollout(
            device_id, result.task_id, result.attempt, result.trace, extracted, accepted
        )
        if accepted and result.task_id not in already_accepted:
            earned += 1
            _archive_accepted(device_id, task, result.trace, extracted)
            already_accepted.add(result.task_id)
        verdicts.append(
            Verdict(task_id=result.task_id, accepted=accepted,
                    extracted_answer=extracted, attempt=result.attempt)
        )
    total = db.add_credits(device_id, earned)
    logger.info(
        "Résultats de %s : %d soumis, %d acceptés (total crédits : %d)",
        device["device_name"], len(payload.results), earned, total,
    )
    return SubmitResponse(verdicts=verdicts, credits_earned=earned, total_credits=total)


@app.get("/stats", response_model=Stats)
def get_stats():
    return Stats(**db.stats())


# --- Dashboard -------------------------------------------------------------

_PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="5">
<title>Essaim — coordinateur</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 640px;
         color: #1a1a1a; background: #fafaf7; }}
  h1 {{ font-size: 1.4rem; }} h1 small {{ color: #999; font-weight: normal; }}
  .cards {{ display: flex; gap: 1rem; flex-wrap: wrap; margin: 1.5rem 0; }}
  .card {{ flex: 1 1 120px; background: white; border: 1px solid #e5e2da;
           border-radius: 8px; padding: 1rem; }}
  .card b {{ display: block; font-size: 1.6rem; }}
  .card span {{ color: #777; font-size: .85rem; }}
  table {{ width: 100%; border-collapse: collapse; background: white;
           border: 1px solid #e5e2da; border-radius: 8px; }}
  th, td {{ text-align: left; padding: .5rem .75rem; border-top: 1px solid #eee; }}
  th {{ border-top: none; color: #777; font-size: .85rem; }}
  footer {{ color: #aaa; font-size: .8rem; margin-top: 1.5rem; }}
</style>
</head>
<body>
<h1>🐝 Essaim <small>— coordinateur (phase 0)</small></h1>
<div class="cards">
  <div class="card"><b>{devices}</b><span>appareils vus</span></div>
  <div class="card"><b>{total}</b><span>rollouts totaux</span></div>
  <div class="card"><b>{accepted}</b><span>rollouts acceptés</span></div>
  <div class="card"><b>{rate:.0%}</b><span>taux d'acceptation</span></div>
</div>
<table>
  <tr><th>#</th><th>Appareil</th><th>Crédits</th></tr>
  {rows}
</table>
<footer>{task_count} tâches GSM8K au catalogue — rafraîchissement auto toutes les 5 s</footer>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def dashboard():
    s = db.stats()
    rows = "".join(
        f"<tr><td>{i + 1}</td><td>{html.escape(c['device_name'])} "
        f"<small style='color:#bbb'>{c['device_id'][:8]}</small></td>"
        f"<td>{c['credits']}</td></tr>"
        for i, c in enumerate(s["top_contributors"])
    ) or "<tr><td colspan=3>Aucun contributeur pour l'instant</td></tr>"
    return _PAGE.format(
        devices=s["devices_seen"],
        total=s["total_rollouts"],
        accepted=s["accepted_rollouts"],
        rate=s["acceptance_rate"],
        rows=rows,
        task_count=tasks.count(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("coordinator.app:app", host=config.HOST, port=config.PORT)
