"""Couche SQLite du coordinateur — stdlib uniquement, une connexion par opération.

À notre échelle (quelques workers), ouvrir une connexion par requête est
largement suffisant et évite tous les soucis de threads de sqlite3.
"""

import secrets
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

from common import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS devices (
    device_id   TEXT PRIMARY KEY,
    api_key     TEXT NOT NULL UNIQUE,
    device_name TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    last_seen   TEXT NOT NULL
);

-- Un compte porte les crédits d'une personne ; un appareil, sa production.
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    handle     TEXT NOT NULL,
    api_key    TEXT NOT NULL UNIQUE,
    credits    INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Un fil de conversation, avec sa mémoire.
CREATE TABLE IF NOT EXISTS conversations (
    id         TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    title      TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_conv_account ON conversations (account_id, updated_at);

CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role            TEXT NOT NULL,
    content         TEXT NOT NULL,
    device_name     TEXT,
    tier            TEXT,
    created_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_msg_conv ON messages (conversation_id, id);

-- Les questions posées depuis le site, servies par les machines du réseau.
CREATE TABLE IF NOT EXISTS questions (
    id              TEXT PRIMARY KEY,
    account_id      TEXT NOT NULL,
    conversation_id TEXT,
    tier            TEXT NOT NULL DEFAULT 'rapide',
    prompt          TEXT NOT NULL,
    status          TEXT NOT NULL,
    answer          TEXT,
    served_by       TEXT,
    device_name     TEXT,
    cost            INTEGER NOT NULL,
    created_at      TEXT NOT NULL,
    claimed_at      TEXT,
    done_at         TEXT
);
CREATE INDEX IF NOT EXISTS idx_questions_status ON questions (status, tier, created_at);

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
        # Les bases nées avant les comptes n'ont pas cette colonne.
        columns = {r["name"] for r in conn.execute("PRAGMA table_info(devices)")}
        if "account_id" not in columns:
            conn.execute("ALTER TABLE devices ADD COLUMN account_id TEXT")
        if "tier" not in columns:
            conn.execute("ALTER TABLE devices ADD COLUMN tier TEXT DEFAULT 'rapide'")


_secret_cache: str | None = None


def server_secret() -> str:
    """Secret de signature des bails, créé au premier démarrage puis persisté
    (un redémarrage n'invalide pas les bails que des workers ont en main)."""
    global _secret_cache
    if _secret_cache is not None:
        return _secret_cache
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM secrets WHERE name = 'lease_key'").fetchone()
        if row is None:
            conn.execute(
                "INSERT OR IGNORE INTO secrets (name, value) VALUES ('lease_key', ?)",
                (secrets.token_hex(32),),
            )
            row = conn.execute(
                "SELECT value FROM secrets WHERE name = 'lease_key'").fetchone()
    _secret_cache = row["value"]
    return _secret_cache


def attempts_for_task(device_id: str, task_id: str) -> int:
    """Tentatives déjà enregistrées pour ce couple — compté par le serveur,
    jamais déclaré par le client (le champ `attempt` sert de pondération à
    l'entraînement : il ne peut pas être laissé à la main du contributeur)."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM rollouts WHERE device_id = ? AND task_id = ?",
            (device_id, task_id),
        ).fetchone()
    return row["n"]


def accepted_count(device_id: str) -> int:
    """Calculs vérifiés au compteur de cet appareil — sa réputation."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM rollouts WHERE device_id = ? AND accepted = 1",
            (device_id,),
        ).fetchone()
    return row["n"]


def submissions_today(device_id: str) -> int:
    """Toutes les soumissions du jour (acceptées OU refusées) : c'est ce
    compteur qui borne l'écriture disque, pas seulement les réussites."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM rollouts WHERE device_id = ?"
            " AND created_at LIKE ?",
            (device_id, f"{today}%"),
        ).fetchone()
    return row["n"]


def register_device(device_name: str, account_id: str | None = None,
                    tier: str = "rapide") -> tuple[str, str]:
    device_id = uuid.uuid4().hex
    api_key = secrets.token_hex(24)
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO devices (device_id, api_key, device_name, created_at, last_seen,"
            " account_id, tier) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (device_id, api_key, device_name, now, now, account_id, tier),
        )
        conn.execute("INSERT INTO credits (device_id, credits) VALUES (?, 0)", (device_id,))
    return device_id, api_key


# --- Comptes ---------------------------------------------------------------


def create_account(handle: str, welcome_credits: int) -> tuple[str, str]:
    """Un compte, une clé. Pas de mot de passe : la clé EST le compte, et on
    offre de quoi essayer l'IA tout de suite."""
    account_id = uuid.uuid4().hex
    api_key = secrets.token_hex(24)
    with _connect() as conn:
        conn.execute(
            "INSERT INTO accounts (account_id, handle, api_key, credits, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (account_id, handle, api_key, welcome_credits, _now()),
        )
    return account_id, api_key


def account_for_key(api_key: str) -> sqlite3.Row | None:
    with _connect() as conn:
        return conn.execute(
            "SELECT * FROM accounts WHERE api_key = ?", (api_key,)).fetchone()


def account_devices(account_id: str) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT d.device_id, d.device_name, d.last_seen, c.credits"
            " FROM devices d LEFT JOIN credits c ON c.device_id = d.device_id"
            " WHERE d.account_id = ? ORDER BY c.credits DESC",
            (account_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def move_account_credits(account_id: str, amount: int) -> int:
    """Ajoute (ou retire, si négatif) des crédits ; renvoie le nouveau solde."""
    with _connect() as conn:
        conn.execute(
            "UPDATE accounts SET credits = credits + ? WHERE account_id = ?",
            (amount, account_id),
        )
        row = conn.execute(
            "SELECT credits FROM accounts WHERE account_id = ?", (account_id,)).fetchone()
    return row["credits"] if row else 0


def spend_credits(account_id: str, amount: int) -> bool:
    """Débit atomique : refuse si le solde est insuffisant."""
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE accounts SET credits = credits - ? WHERE account_id = ? AND credits >= ?",
            (amount, account_id, amount),
        )
        return cur.rowcount == 1


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
    """Ajoute des crédits à l'appareil ET au compte qui le porte, s'il y en a un.
    L'appareil garde son compteur (le classement), le compte tient la bourse."""
    with _connect() as conn:
        conn.execute(
            "UPDATE credits SET credits = credits + ? WHERE device_id = ?",
            (amount, device_id),
        )
        row = conn.execute(
            "SELECT credits FROM credits WHERE device_id = ?", (device_id,)
        ).fetchone()
        owner = conn.execute(
            "SELECT account_id FROM devices WHERE device_id = ?", (device_id,)
        ).fetchone()
        if amount and owner and owner["account_id"]:
            conn.execute(
                "UPDATE accounts SET credits = credits + ? WHERE account_id = ?",
                (amount, owner["account_id"]),
            )
    return row["credits"] if row else 0


# --- Questions posées au réseau --------------------------------------------


def create_question(account_id: str, prompt: str, cost: int,
                    conversation_id: str | None = None, tier: str = "rapide") -> str:
    question_id = uuid.uuid4().hex[:16]
    with _connect() as conn:
        conn.execute(
            "INSERT INTO questions (id, account_id, conversation_id, tier, prompt,"
            " status, cost, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)",
            (question_id, account_id, conversation_id, tier, prompt, cost, _now()),
        )
    return question_id


# --- Conversations ----------------------------------------------------------


def create_conversation(account_id: str, title: str = "Nouvelle conversation") -> dict:
    conversation_id = uuid.uuid4().hex[:16]
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO conversations (id, account_id, title, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (conversation_id, account_id, title, now, now),
        )
    return {"id": conversation_id, "title": title, "updated_at": now}


def list_conversations(account_id: str, limit: int = 60) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, title, updated_at FROM conversations WHERE account_id = ?"
            " ORDER BY updated_at DESC LIMIT ?",
            (account_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def get_conversation(conversation_id: str, account_id: str) -> sqlite3.Row | None:
    """Toujours filtré sur le compte : un fil n'appartient qu'à son auteur."""
    with _connect() as conn:
        return conn.execute(
            "SELECT * FROM conversations WHERE id = ? AND account_id = ?",
            (conversation_id, account_id),
        ).fetchone()


def delete_conversation(conversation_id: str, account_id: str) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM conversations WHERE id = ? AND account_id = ?",
            (conversation_id, account_id),
        )
        if cur.rowcount:
            conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        return cur.rowcount == 1


def add_message(conversation_id: str, role: str, content: str,
                device_name: str | None = None, tier: str | None = None) -> None:
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, device_name, tier,"
            " created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (conversation_id, role, content, device_name, tier, now),
        )
        conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?",
                     (now, conversation_id))


def conversation_messages(conversation_id: str, limit: int | None = None) -> list[dict]:
    query = ("SELECT role, content, device_name, tier, created_at FROM messages"
             " WHERE conversation_id = ? ORDER BY id")
    with _connect() as conn:
        rows = conn.execute(query, (conversation_id,)).fetchall()
    messages = [dict(r) for r in rows]
    return messages[-limit:] if limit else messages


def set_conversation_title(conversation_id: str, title: str) -> None:
    with _connect() as conn:
        conn.execute("UPDATE conversations SET title = ? WHERE id = ?",
                     (title, conversation_id))


def get_question(question_id: str) -> sqlite3.Row | None:
    with _connect() as conn:
        return conn.execute(
            "SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()


def claim_question(device_id: str, device_name: str,
                   tier: str = "rapide") -> sqlite3.Row | None:
    """Attribue la plus ancienne question EN ATTENTE DE CE PALIER à cet appareil.

    La mise à jour conditionnelle fait office de verrou : deux machines qui
    tirent en même temps ne peuvent pas décrocher la même question.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM questions WHERE status = 'pending' AND tier = ?"
            " ORDER BY created_at LIMIT 1", (tier,)).fetchone()
        if row is None:
            return None
        cur = conn.execute(
            "UPDATE questions SET status = 'serving', served_by = ?, device_name = ?,"
            " claimed_at = ? WHERE id = ? AND status = 'pending'",
            (device_id, device_name, _now(), row["id"]),
        )
        if cur.rowcount != 1:
            return None
        return conn.execute("SELECT * FROM questions WHERE id = ?", (row["id"],)).fetchone()


def answer_question(question_id: str, device_id: str, answer: str) -> bool:
    """N'accepte la réponse que de la machine qui a décroché la question."""
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE questions SET status = 'done', answer = ?, done_at = ?"
            " WHERE id = ? AND status = 'serving' AND served_by = ?",
            (answer, _now(), question_id, device_id),
        )
        return cur.rowcount == 1


def release_stale_questions(seconds: int) -> int:
    """Une machine qui décroche puis disparaît ne doit pas bloquer la question."""
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat()
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE questions SET status = 'pending', served_by = NULL, device_name = NULL,"
            " claimed_at = NULL WHERE status = 'serving' AND claimed_at < ?",
            (cutoff,),
        )
        return cur.rowcount


def recent_questions(account_id: str, limit: int = 20) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, prompt, status, answer, device_name, cost, created_at"
            " FROM questions WHERE account_id = ? ORDER BY created_at DESC LIMIT ?",
            (account_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


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
    """Tâches jamais résolues et ratées par plusieurs appareils DISTINCTS —
    cibles du mode chasse. Le seuil évite qu'un seul client oriente tout
    l'essaim en soumettant des réponses fausses en rafale."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT task_id FROM rollouts GROUP BY task_id"
            " HAVING MAX(accepted) = 0 AND COUNT(DISTINCT device_id) >= ?",
            (config.HARD_MIN_DEVICES,),
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
