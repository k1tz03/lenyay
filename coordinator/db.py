"""Couche SQLite du coordinateur — stdlib uniquement, une connexion par opération.

À notre échelle (quelques workers), ouvrir une connexion par requête est
largement suffisant et évite tous les soucis de threads de sqlite3.
"""

import secrets
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from common import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS devices (
    device_id   TEXT PRIMARY KEY,
    api_key     TEXT NOT NULL UNIQUE,
    device_name TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    last_seen   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS secrets (
    name  TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS credits (
    device_id TEXT PRIMARY KEY REFERENCES devices(device_id),
    credits   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS rollouts (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id        TEXT NOT NULL,
    task_id          TEXT NOT NULL,
    attempt          INTEGER NOT NULL,
    trace            TEXT NOT NULL,
    extracted_answer TEXT,
    accepted         INTEGER NOT NULL,
    created_at       TEXT NOT NULL
);

-- Sans ces index, chaque requête authentifiée fait un scan complet d'une
-- table qui grossit sans borne (accepted_task_ids, accepted_today, stats).
CREATE INDEX IF NOT EXISTS idx_rollouts_device_accepted
    ON rollouts (device_id, accepted);
CREATE INDEX IF NOT EXISTS idx_rollouts_task_accepted
    ON rollouts (task_id, accepted);
CREATE INDEX IF NOT EXISTS idx_rollouts_accepted
    ON rollouts (accepted);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _connect():
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # timeout : attendre le writer plutôt que lever « database is locked ».
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    # WAL : lecteurs (dashboard) et writer (workers) ne se bloquent plus.
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _adopt_legacy_db() -> None:
    """Premier démarrage sous le nom Lenyay : adopte l'ancienne base Essaim
    (essaim.db, même dossier) au lieu de repartir de zéro. Ne s'exécute qu'au
    démarrage du coordinateur — jamais pendant qu'un autre tourne dessus."""
    if config.DB_PATH.exists():
        return
    legacy = config.DB_PATH.with_name("essaim.db")
    if legacy.exists():
        legacy.rename(config.DB_PATH)


def init_db() -> None:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    _adopt_legacy_db()
    with _connect() as conn:
        conn.executescript(_SCHEMA)


def server_secret() -> str:
    """Secret de signature des bails, créé au premier démarrage puis persisté
    (un redémarrage n'invalide pas les bails que des workers ont en main)."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM secrets WHERE name = 'lease_key'").fetchone()
        if row is not None:
            return row["value"]
        secret = secrets.token_hex(32)
        conn.execute(
            "INSERT OR IGNORE INTO secrets (name, value) VALUES ('lease_key', ?)",
            (secret,),
        )
        row = conn.execute(
            "SELECT value FROM secrets WHERE name = 'lease_key'").fetchone()
    return row["value"]


def archived_count_for_task(task_id: str) -> int:
    """Nombre d'appareils distincts ayant fait accepter cette tâche — donc le
    nombre de traces déjà versées au dataset pour elle."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(DISTINCT device_id) AS n FROM rollouts"
            " WHERE task_id = ? AND accepted = 1",
            (task_id,),
        ).fetchone()
    return row["n"]


def register_device(device_name: str) -> tuple[str, str]:
    device_id = uuid.uuid4().hex
    api_key = secrets.token_hex(24)
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO devices (device_id, api_key, device_name, created_at, last_seen)"
            " VALUES (?, ?, ?, ?, ?)",
            (device_id, api_key, device_name, now, now),
        )
        conn.execute("INSERT INTO credits (device_id, credits) VALUES (?, 0)", (device_id,))
    return device_id, api_key


def device_for_key(api_key: str) -> sqlite3.Row | None:
    """Renvoie l'appareil associé à la clé (et met à jour last_seen), sinon None."""
    with _connect() as conn:
        row = conn.execute("SELECT * FROM devices WHERE api_key = ?", (api_key,)).fetchone()
        if row is not None:
            conn.execute(
                "UPDATE devices SET last_seen = ? WHERE device_id = ?",
                (_now(), row["device_id"]),
            )
    return row


def record_rollout(
    device_id: str,
    task_id: str,
    attempt: int,
    trace: str,
    extracted_answer: str | None,
    accepted: bool,
) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO rollouts (device_id, task_id, attempt, trace, extracted_answer,"
            " accepted, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (device_id, task_id, attempt, trace, extracted_answer, int(accepted), _now()),
        )


def add_credits(device_id: str, amount: int) -> int:
    """Ajoute des crédits et renvoie le nouveau total."""
    with _connect() as conn:
        conn.execute(
            "UPDATE credits SET credits = credits + ? WHERE device_id = ?",
            (amount, device_id),
        )
        row = conn.execute(
            "SELECT credits FROM credits WHERE device_id = ?", (device_id,)
        ).fetchone()
    return row["credits"] if row else 0


def accepted_today(device_id: str) -> int:
    """Rollouts acceptés aujourd'hui (UTC) — sert de compteur au plafond
    quotidien de crédits. Approximation honnête : le worker ne re-soumet
    jamais une tâche déjà acceptée, donc acceptés ≈ crédités."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM rollouts WHERE device_id = ?"
            " AND accepted = 1 AND created_at LIKE ?",
            (device_id, f"{today}%"),
        ).fetchone()
    return row["n"]


def hard_task_ids() -> set[str]:
    """Tâches déjà tentées mais jamais résolues par personne — cibles du mode
    chasse : c'est là que naissent les traces « durement gagnées »."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT task_id FROM rollouts GROUP BY task_id HAVING MAX(accepted) = 0"
        ).fetchall()
    return {r["task_id"] for r in rows}


def accepted_task_ids(device_id: str) -> set[str]:
    """Tâches déjà résolues par cet appareil — pour ne pas les lui re-servir."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT task_id FROM rollouts WHERE device_id = ? AND accepted = 1",
            (device_id,),
        ).fetchall()
    return {r["task_id"] for r in rows}


def stats(top_n: int = 10) -> dict:
    with _connect() as conn:
        devices_seen = conn.execute("SELECT COUNT(*) AS n FROM devices").fetchone()["n"]
        total = conn.execute("SELECT COUNT(*) AS n FROM rollouts").fetchone()["n"]
        accepted = conn.execute(
            "SELECT COUNT(*) AS n FROM rollouts WHERE accepted = 1"
        ).fetchone()["n"]
        total_credits = conn.execute(
            "SELECT COALESCE(SUM(credits), 0) AS n FROM credits"
        ).fetchone()["n"]
        top = conn.execute(
            "SELECT c.device_id, d.device_name, c.credits, d.last_seen"
            " FROM credits c JOIN devices d ON d.device_id = c.device_id"
            " ORDER BY c.credits DESC, d.device_name LIMIT ?",
            (top_n,),
        ).fetchall()
    return {
        "devices_seen": devices_seen,
        "total_rollouts": total,
        "accepted_rollouts": accepted,
        "acceptance_rate": (accepted / total) if total else 0.0,
        "total_credits": total_credits,
        "top_contributors": [dict(r) for r in top],
    }
