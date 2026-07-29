"""Coordinateur Lenyay — API FastAPI + mini-dashboard HTML.

Lancement :  python -m coordinator.app
(LENYAY_HOST / LENYAY_PORT pris en compte ; avec la CLI uvicorn, passer
soi-même --host/--port.)
"""

import json
import logging
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
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
from coordinator import db, limits, tasks
from coordinator.verifier import verify

logger = logging.getLogger("lenyay.coordinator")
_archive_lock = threading.Lock()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    db.init_db()
    n = tasks.load_tasks()
    config.ACCEPTED_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Coordinateur prêt : %d tâches chargées, base %s", n, config.DB_PATH)
    yield


app = FastAPI(title="Lenyay — coordinateur", lifespan=lifespan)


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


@app.post("/devices/register", response_model=RegisterResponse)
def register(payload: RegisterRequest, request: Request):
    client_ip = request.client.host if request.client else "inconnue"
    if not limits.register_limiter.allow(client_ip, config.REGISTER_LIMIT, 3600.0):
        raise HTTPException(
            status_code=429,
            detail="Trop d'enregistrements depuis cette adresse — réessaie plus tard",
        )
    device_id, api_key = db.register_device(payload.device_name)
    logger.info("Nouvel appareil enregistré : %s (%s)", payload.device_name, device_id[:8])
    return RegisterResponse(device_id=device_id, api_key=api_key)


@app.get("/work", response_model=WorkBatch)
def get_work(
    n: int = Query(default=config.BATCH_SIZE, ge=1, le=32),
    device=Depends(require_device),
):
    solved = db.accepted_task_ids(device["device_id"])
    hard = db.hard_task_ids() if config.HUNT_MODE else None
    batch = tasks.sample(n, exclude=solved, hard_first=hard)
    # Task (sans expected_answer) : la réponse attendue ne sort JAMAIS d'ici.
    return WorkBatch(tasks=[Task(task_id=t.task_id, prompt=t.prompt) for t in batch])


@app.post("/results", response_model=SubmitResponse)
def submit_results(payload: ResultsPayload, device=Depends(require_device)):
    device_id = device["device_id"]
    # Une tâche déjà acceptée par cet appareil ne rapporte plus rien : pas de
    # nouveau crédit, pas de doublon dans le dataset (le rollout reste journalisé).
    already_accepted = db.accepted_task_ids(device_id)
    credited_today = db.accepted_today(device_id)
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
        if accepted and len(result.trace.strip()) < config.MIN_TRACE_CHARS:
            # Bonne réponse sans raisonnement : aucune valeur pour le dataset,
            # et signature classique d'une réponse copiée. Pas de crédit.
            accepted = False
            logger.info("Trace creuse refusée : %s sur %s",
                        device["device_name"], result.task_id)
        db.record_rollout(
            device_id, result.task_id, result.attempt, result.trace, extracted, accepted
        )
        if accepted and result.task_id not in already_accepted:
            if config.DAILY_CREDIT_CAP and credited_today + earned >= config.DAILY_CREDIT_CAP:
                # Plafond quotidien : le verdict reste honnête, mais ni crédit
                # ni entrée au dataset (anti-farming).
                logger.info("Plafond quotidien atteint pour %s", device["device_name"])
            else:
                earned += 1
                _archive_accepted(device_id, task, result.trace, extracted, result.attempt)
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
def dashboard():
    return _PAGE


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("coordinator.app:app", host=config.HOST, port=config.PORT)
