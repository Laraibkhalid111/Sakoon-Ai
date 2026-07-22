"""
database.py — Sakoon AI
SQLite persistence layer (sakoon.db). Implements schema creation for the
4 flat tables from IDEA.md §6 (users, sessions, messages, symptom_snapshots)
and all CRUD helpers called by app.py per conversation turn.

Design rules:
  - All writes wrapped in try/except so a failure never interrupts the chat.
  - Returns None / empty on failure; caller shows non-alarming banner copy.
  - Zero external deps beyond Python stdlib sqlite3.
  - DB file: sakoon.db (gitignored).
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

from sakoon.core.logging import get_logger
from sakoon.core.paths import DB_PATH as _DEFAULT_DB_PATH

# Overridable for tests (monkeypatch sakoon.db.database.DB_PATH)
DB_PATH: Path = _DEFAULT_DB_PATH

# Process-local guard: skip full schema script after first success per DB path
_SCHEMA_READY_FOR: Path | None = None

log = get_logger(__name__)

# ── Schema ────────────────────────────────────────────────────────────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT,
    email            TEXT,
    phone            TEXT,
    preferred_language TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER,
    started_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at         TIMESTAMP,
    primary_concern  TEXT,
    title            TEXT,
    risk_level       TEXT DEFAULT 'low',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       INTEGER,
    role             TEXT,
    content          TEXT,
    input_mode       TEXT DEFAULT 'text',
    timestamp        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS symptom_snapshots (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id            INTEGER UNIQUE,
    mood_rating           INTEGER,
    symptoms_json         TEXT,
    triggers_json         TEXT,
    coping_suggestions_json TEXT,
    updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_session_id ON symptom_snapshots(session_id);

CREATE TABLE IF NOT EXISTS mood_logs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       INTEGER,
    user_id          INTEGER,
    rating           INTEGER NOT NULL,
    note             TEXT,
    source           TEXT DEFAULT 'manual',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       INTEGER,
    user_id          INTEGER,
    prompt           TEXT,
    body             TEXT NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_mood_logs_created ON mood_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_mood_logs_session ON mood_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_journal_created ON journal_entries(created_at);
CREATE INDEX IF NOT EXISTS idx_journal_session ON journal_entries(session_id);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def init_db() -> bool:
    """
    Create all tables if they don't exist. Safe to call often — skips heavy
    schema script once applied for the current DB_PATH in this process, but
    always runs lightweight column migrations.
    Returns True on success, False on failure.
    """
    global _SCHEMA_READY_FOR
    try:
        already = _SCHEMA_READY_FOR == DB_PATH and Path(DB_PATH).exists()
        with _connect() as conn:
            if not already:
                conn.executescript(_SCHEMA)
            _migrate_schema(conn)
        _SCHEMA_READY_FOR = DB_PATH
        return True
    except Exception as e:
        log.error("init_db failed: %s", e)
        return False


def _migrate_schema(conn: sqlite3.Connection) -> None:
    """Additive migrations for existing SQLite files."""
    _migrate_auth_columns(conn)
    _migrate_session_title(conn)


def _migrate_session_title(conn: sqlite3.Connection) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()}
    if "title" not in cols:
        conn.execute("ALTER TABLE sessions ADD COLUMN title TEXT")


def _migrate_auth_columns(conn: sqlite3.Connection) -> None:
    """Add username/password_hash for multi-user auth (Phase 5) on existing DBs."""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
    if "username" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN username TEXT")
    if "password_hash" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username "
        "ON users(username) WHERE username IS NOT NULL"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mood_logs_user ON mood_logs(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_journal_user ON journal_entries(user_id)")


# ── Users ─────────────────────────────────────────────────────────────────────

def upsert_user(name: str | None, email: str | None, phone: str | None,
                preferred_language: str = "english") -> int | None:
    """
    True upsert: if a matching email exists, update that row; otherwise insert.
    When email is missing, inserts a new row (anonymous / name-only contact).
    Returns the user id, or None on failure.
    """
    try:
        with _connect() as conn:
            email_norm = (email or "").strip().lower() or None
            if email_norm:
                row = conn.execute(
                    "SELECT id FROM users WHERE lower(email) = ? LIMIT 1",
                    (email_norm,),
                ).fetchone()
                if row:
                    conn.execute(
                        """UPDATE users
                           SET name = COALESCE(?, name),
                               email = ?,
                               phone = COALESCE(?, phone),
                               preferred_language = ?
                           WHERE id = ?""",
                        (name, email_norm, phone, preferred_language, row["id"]),
                    )
                    return int(row["id"])

            cur = conn.execute(
                "INSERT INTO users (name, email, phone, preferred_language) VALUES (?, ?, ?, ?)",
                (name, email_norm, phone, preferred_language),
            )
            return cur.lastrowid
    except Exception as e:
        log.error("upsert_user failed: %s", e)
        return None


# Stable local device profile (no accounts / passwords)
_LOCAL_USERNAME = "__local__"
_LOCAL_NAME = "Local"


def get_or_create_local_user(preferred_language: str = "english") -> int | None:
    """
    Return the single local device user id used when auth is disabled.
    Identified by username=__local__ so contact email updates never lose the row.
    """
    try:
        with _connect() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE username = ? LIMIT 1",
                (_LOCAL_USERNAME,),
            ).fetchone()
            if row:
                return int(row["id"])
            cur = conn.execute(
                """INSERT INTO users (username, password_hash, name, email, phone, preferred_language)
                   VALUES (?, NULL, ?, NULL, NULL, ?)""",
                (_LOCAL_USERNAME, _LOCAL_NAME, preferred_language),
            )
            return cur.lastrowid
    except Exception as e:
        log.error("get_or_create_local_user failed: %s", e)
        return None


def update_user(user_id: int, name: str | None = None, email: str | None = None,
                phone: str | None = None, preferred_language: str | None = None) -> bool:
    """Update non-null fields on an existing user row."""
    updates, values = [], []
    if name is not None:
        updates.append("name = ?"); values.append(name)
    if email is not None:
        updates.append("email = ?"); values.append(email)
    if phone is not None:
        updates.append("phone = ?"); values.append(phone)
    if preferred_language is not None:
        updates.append("preferred_language = ?"); values.append(preferred_language)
    if not updates:
        return True
    try:
        with _connect() as conn:
            conn.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                (*values, user_id),
            )
        return True
    except Exception as e:
        log.error("update_user failed: %s", e)
        return False


def create_auth_user(
    username: str,
    password_hash: str,
    name: str | None = None,
    email: str | None = None,
    preferred_language: str = "english",
) -> int | None:
    """Create a registered user account. Username must be unique."""
    try:
        uname = (username or "").strip().lower()
        if not uname or not password_hash:
            return None
        with _connect() as conn:
            existing = conn.execute(
                "SELECT id FROM users WHERE lower(username) = ? LIMIT 1", (uname,)
            ).fetchone()
            if existing:
                return None
            email_norm = (email or "").strip().lower() or None
            cur = conn.execute(
                """INSERT INTO users (username, password_hash, name, email, preferred_language)
                   VALUES (?, ?, ?, ?, ?)""",
                (uname, password_hash, name, email_norm, preferred_language),
            )
            return cur.lastrowid
    except Exception as e:
        log.error("create_auth_user failed: %s", e)
        return None


def get_user_by_username(username: str) -> dict | None:
    """Return auth user row by username (includes password_hash)."""
    try:
        uname = (username or "").strip().lower()
        if not uname:
            return None
        with _connect() as conn:
            row = conn.execute(
                """SELECT id, username, password_hash, name, email, phone, preferred_language
                   FROM users WHERE lower(username) = ? LIMIT 1""",
                (uname,),
            ).fetchone()
            return dict(row) if row else None
    except Exception as e:
        log.error("get_user_by_username failed: %s", e)
        return None


def get_user_by_id(user_id: int) -> dict | None:
    """Return public user fields (no password hash)."""
    try:
        with _connect() as conn:
            row = conn.execute(
                """SELECT id, username, name, email, phone, preferred_language
                   FROM users WHERE id = ? LIMIT 1""",
                (user_id,),
            ).fetchone()
            return dict(row) if row else None
    except Exception as e:
        log.error("get_user_by_id failed: %s", e)
        return None


def session_belongs_to_user(session_id: int, user_id: int) -> bool:
    """Authorization check: session owned by user."""
    try:
        with _connect() as conn:
            row = conn.execute(
                "SELECT id FROM sessions WHERE id = ? AND user_id = ? LIMIT 1",
                (session_id, user_id),
            ).fetchone()
            return row is not None
    except Exception as e:
        log.error("session_belongs_to_user failed: %s", e)
        return False


# ── Sessions ──────────────────────────────────────────────────────────────────

def create_session(user_id: int | None) -> int | None:
    """
    Create a new session row. user_id may be None until contact info arrives.
    Returns the new session id, or None on failure.
    """
    try:
        with _connect() as conn:
            cur = conn.execute(
                "INSERT INTO sessions (user_id) VALUES (?)", (user_id,)
            )
            return cur.lastrowid
    except Exception as e:
        log.error("create_session failed: %s", e)
        return None


def update_session(session_id: int, user_id: int | None = None,
                   primary_concern: str | None = None,
                   risk_level: str | None = None,
                   ended_at: str | None = None,
                   title: str | None = None) -> bool:
    """Update mutable fields on an existing session row."""
    updates, values = [], []
    if user_id is not None:
        updates.append("user_id = ?"); values.append(user_id)
    if primary_concern is not None:
        updates.append("primary_concern = ?"); values.append(primary_concern)
    if risk_level is not None:
        updates.append("risk_level = ?"); values.append(risk_level)
    if ended_at is not None:
        updates.append("ended_at = ?"); values.append(ended_at)
    if title is not None:
        updates.append("title = ?"); values.append(title)
    if not updates:
        return True
    try:
        with _connect() as conn:
            conn.execute(
                f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?",
                (*values, session_id),
            )
        return True
    except Exception as e:
        log.error("update_session failed: %s", e)
        return False


def close_session(session_id: int) -> bool:
    """Mark a session as ended with the current timestamp."""
    return update_session(session_id, ended_at=_utc_now())


def rename_session(session_id: int, user_id: int, title: str) -> bool:
    """Set a custom conversation title (local ChatGPT-lite rename)."""
    clean = (title or "").strip()
    if not clean or not session_belongs_to_user(session_id, user_id):
        return False
    if len(clean) > 120:
        clean = clean[:120].rstrip()
    return update_session(session_id, title=clean)


def ensure_session_title_from_text(session_id: int, text: str) -> bool:
    """
    If the session has no title yet, set one from the first user message snippet.
    Does not overwrite a user-renamed title.
    """
    snippet = " ".join((text or "").strip().split())
    if not snippet:
        return False
    if len(snippet) > 60:
        snippet = snippet[:57].rstrip() + "…"
    try:
        with _connect() as conn:
            row = conn.execute(
                "SELECT title FROM sessions WHERE id = ? LIMIT 1",
                (session_id,),
            ).fetchone()
            if not row or (row["title"] or "").strip():
                return False
            conn.execute(
                "UPDATE sessions SET title = ? WHERE id = ?",
                (snippet, session_id),
            )
        return True
    except Exception as e:
        log.error("ensure_session_title_from_text failed: %s", e)
        return False


def delete_session(session_id: int, user_id: int) -> bool:
    """
    Delete a conversation owned by user_id.
    Removes messages + snapshot; detaches mood/journal rows (keeps wellness data).
    """
    if not session_belongs_to_user(session_id, user_id):
        return False
    try:
        with _connect() as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM symptom_snapshots WHERE session_id = ?", (session_id,))
            conn.execute(
                "UPDATE mood_logs SET session_id = NULL WHERE session_id = ?",
                (session_id,),
            )
            conn.execute(
                "UPDATE journal_entries SET session_id = NULL WHERE session_id = ?",
                (session_id,),
            )
            cur = conn.execute(
                "DELETE FROM sessions WHERE id = ? AND user_id = ?",
                (session_id, user_id),
            )
            return cur.rowcount > 0
    except Exception as e:
        log.error("delete_session failed: %s", e)
        return False


def export_session_markdown(session_id: int, user_id: int) -> str | None:
    """Export an owned session as Markdown text, or None if missing/unauthorized."""
    if not session_belongs_to_user(session_id, user_id):
        return None
    try:
        with _connect() as conn:
            meta = conn.execute(
                """SELECT id, title, primary_concern, started_at, risk_level
                   FROM sessions WHERE id = ? LIMIT 1""",
                (session_id,),
            ).fetchone()
            if not meta:
                return None
            rows = conn.execute(
                """SELECT role, content, input_mode, timestamp
                   FROM messages WHERE session_id = ?
                   ORDER BY id ASC""",
                (session_id,),
            ).fetchall()
        title = (
            (meta["title"] or "").strip()
            or (meta["primary_concern"] or "").strip()
            or f"Session #{meta['id']}"
        )
        lines = [
            f"# {title}",
            "",
            f"- Session id: {meta['id']}",
            f"- Started: {meta['started_at'] or '—'}",
            f"- Risk: {meta['risk_level'] or 'low'}",
            "",
            "---",
            "",
        ]
        for row in rows:
            role = (row["role"] or "assistant").strip().lower()
            who = "You" if role == "user" else "Sakoon"
            mode = row["input_mode"] or "text"
            stamp = row["timestamp"] or ""
            header = f"### {who}"
            if stamp:
                header += f" · {stamp}"
            if mode == "voice" and role == "user":
                header += " · voice"
            lines.append(header)
            lines.append("")
            lines.append((row["content"] or "").strip() or "_(empty)_")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"
    except Exception as e:
        log.error("export_session_markdown failed: %s", e)
        return None


def session_label(row: dict) -> str:
    """Human label for sidebar history rows."""
    title = (row.get("title") or "").strip()
    if title:
        return title
    concern = (row.get("primary_concern") or "").strip()
    if concern:
        return concern
    name = (row.get("name") or "").strip()
    if name and name.lower() not in ("local", "__local__"):
        return name
    sid = row.get("id")
    return f"Session #{sid}" if sid is not None else "Session"


# ── Messages ──────────────────────────────────────────────────────────────────

def log_message(session_id: int, role: str, content: str,
                input_mode: str = "text") -> int | None:
    """
    Append one message row. role = 'user' | 'assistant'.
    Returns the new message id, or None on failure.
    """
    try:
        with _connect() as conn:
            cur = conn.execute(
                "INSERT INTO messages (session_id, role, content, input_mode) VALUES (?, ?, ?, ?)",
                (session_id, role, content, input_mode),
            )
            return cur.lastrowid
    except Exception as e:
        log.error("log_message failed: %s", e)
        return None


def delete_last_assistant_message(session_id: int) -> bool:
    """Remove the latest assistant message for a session (used by regenerate)."""
    try:
        with _connect() as conn:
            row = conn.execute(
                """SELECT id FROM messages
                   WHERE session_id = ? AND role = 'assistant'
                   ORDER BY id DESC LIMIT 1""",
                (session_id,),
            ).fetchone()
            if not row:
                return True
            conn.execute("DELETE FROM messages WHERE id = ?", (row["id"],))
            return True
    except Exception as e:
        log.error("delete_last_assistant_message failed: %s", e)
        return False


def get_messages(session_id: int) -> list[dict]:
    """Return all messages for a session as a list of dicts."""
    try:
        with _connect() as conn:
            rows = conn.execute(
                "SELECT role, content, input_mode, timestamp FROM messages "
                "WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        log.error("get_messages failed: %s", e)
        return []


# ── Symptom Snapshots ─────────────────────────────────────────────────────────

def upsert_snapshot(session_id: int, mood_rating: int | None,
                    symptoms: list, triggers: list,
                    coping_suggestions: list) -> bool:
    """
    Upsert the symptom snapshot for a session — one row per session,
    replaced entirely on each update (accumulated data from app.py).
    Returns True on success, False on failure.
    """
    try:
        with _connect() as conn:
            existing = conn.execute(
                "SELECT id FROM symptom_snapshots WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            now = _utc_now()
            if existing:
                conn.execute(
                    """UPDATE symptom_snapshots
                       SET mood_rating=?, symptoms_json=?, triggers_json=?,
                           coping_suggestions_json=?, updated_at=?
                       WHERE session_id=?""",
                    (
                        mood_rating,
                        json.dumps(symptoms, ensure_ascii=False),
                        json.dumps(triggers, ensure_ascii=False),
                        json.dumps(coping_suggestions, ensure_ascii=False),
                        now,
                        session_id,
                    ),
                )
            else:
                conn.execute(
                    """INSERT INTO symptom_snapshots
                       (session_id, mood_rating, symptoms_json, triggers_json,
                        coping_suggestions_json, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        session_id,
                        mood_rating,
                        json.dumps(symptoms, ensure_ascii=False),
                        json.dumps(triggers, ensure_ascii=False),
                        json.dumps(coping_suggestions, ensure_ascii=False),
                        now,
                    ),
                )
        return True
    except Exception as e:
        log.error("upsert_snapshot failed: %s", e)
        return False


def get_snapshot(session_id: int) -> dict | None:
    """Return the symptom snapshot for a session as a dict, or None."""
    try:
        with _connect() as conn:
            row = conn.execute(
                "SELECT * FROM symptom_snapshots WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            for field in ("symptoms_json", "triggers_json", "coping_suggestions_json"):
                try:
                    d[field] = json.loads(d[field] or "[]")
                except (json.JSONDecodeError, TypeError):
                    d[field] = []
            return d
    except Exception as e:
        log.error("get_snapshot failed: %s", e)
        return None


# ── Past sessions (optional sidebar feature, T3.5) ────────────────────────────

def get_recent_sessions(limit: int = 5, user_id: int | None = None) -> list[dict]:
    """
    Return the most recent N sessions with their user name and primary concern.
    When user_id is set, only that user's sessions are returned (Phase 5 isolation).
    """
    try:
        with _connect() as conn:
            if user_id is not None:
                rows = conn.execute(
                    """SELECT s.id, u.name, s.title, s.primary_concern, s.started_at, s.risk_level
                       FROM sessions s
                       LEFT JOIN users u ON u.id = s.user_id
                       WHERE s.user_id = ?
                       ORDER BY s.started_at DESC
                       LIMIT ?""",
                    (user_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT s.id, u.name, s.title, s.primary_concern, s.started_at, s.risk_level
                       FROM sessions s
                       LEFT JOIN users u ON u.id = s.user_id
                       ORDER BY s.started_at DESC
                       LIMIT ?""",
                    (limit,),
                ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        log.error("get_recent_sessions failed: %s", e)
        return []


# ── Mood logs (Phase 3) ───────────────────────────────────────────────────────

def add_mood_log(
    rating: int,
    note: str | None = None,
    session_id: int | None = None,
    user_id: int | None = None,
    source: str = "manual",
) -> int | None:
    """Insert a mood log (1–10). Returns new id or None."""
    try:
        rating = max(1, min(10, int(rating)))
        with _connect() as conn:
            cur = conn.execute(
                """INSERT INTO mood_logs (session_id, user_id, rating, note, source, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (session_id, user_id, rating, (note or "").strip() or None, source, _utc_now()),
            )
            return cur.lastrowid
    except Exception as e:
        log.error("add_mood_log failed: %s", e)
        return None


def get_mood_logs(
    limit: int = 30,
    session_id: int | None = None,
    user_id: int | None = None,
) -> list[dict]:
    """Return recent mood logs, filtered by user and/or session."""
    try:
        with _connect() as conn:
            clauses, params = [], []
            if user_id is not None:
                clauses.append("user_id = ?")
                params.append(user_id)
            if session_id is not None:
                clauses.append("session_id = ?")
                params.append(session_id)
            where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            params.append(limit)
            rows = conn.execute(
                f"""SELECT id, session_id, rating, note, source, created_at
                    FROM mood_logs {where}
                    ORDER BY created_at DESC, id DESC LIMIT ?""",
                tuple(params),
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        log.error("get_mood_logs failed: %s", e)
        return []


# ── Journal entries (Phase 3) ─────────────────────────────────────────────────

def add_journal_entry(
    body: str,
    prompt: str | None = None,
    session_id: int | None = None,
    user_id: int | None = None,
) -> int | None:
    """Persist a journal note (optionally encrypted at rest). Returns new id or None."""
    try:
        text = (body or "").strip()
        if not text:
            return None
        from sakoon.core.crypto import encrypt_text

        stored = encrypt_text(text)
        with _connect() as conn:
            cur = conn.execute(
                """INSERT INTO journal_entries (session_id, user_id, prompt, body, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, user_id, prompt, stored, _utc_now()),
            )
            return cur.lastrowid
    except Exception as e:
        log.error("add_journal_entry failed: %s", e)
        return None


def get_journal_entries(
    limit: int = 20,
    session_id: int | None = None,
    user_id: int | None = None,
) -> list[dict]:
    """Return recent journal entries (decrypted when encryption is enabled)."""
    try:
        from sakoon.core.crypto import decrypt_text

        with _connect() as conn:
            clauses, params = [], []
            if user_id is not None:
                clauses.append("user_id = ?")
                params.append(user_id)
            if session_id is not None:
                clauses.append("session_id = ?")
                params.append(session_id)
            where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            params.append(limit)
            rows = conn.execute(
                f"""SELECT id, session_id, prompt, body, created_at
                    FROM journal_entries {where}
                    ORDER BY created_at DESC, id DESC LIMIT ?""",
                tuple(params),
            ).fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["body"] = decrypt_text(d.get("body") or "")
                out.append(d)
            return out
    except Exception as e:
        log.error("get_journal_entries failed: %s", e)
        return []


# ── Analytics (Phase 4 / 5) ───────────────────────────────────────────────────

def get_mood_daily_averages(days: int = 30, user_id: int | None = None) -> list[dict]:
    """Average mood rating per calendar day for the last N days (optionally per user)."""
    try:
        days = max(1, min(365, int(days)))
        with _connect() as conn:
            if user_id is not None:
                rows = conn.execute(
                    """SELECT date(created_at) AS day,
                              ROUND(AVG(rating), 2) AS avg_rating,
                              COUNT(*) AS count
                       FROM mood_logs
                       WHERE user_id = ? AND date(created_at) >= date('now', ?)
                       GROUP BY date(created_at)
                       ORDER BY day ASC""",
                    (user_id, f"-{days} days"),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT date(created_at) AS day,
                              ROUND(AVG(rating), 2) AS avg_rating,
                              COUNT(*) AS count
                       FROM mood_logs
                       WHERE date(created_at) >= date('now', ?)
                       GROUP BY date(created_at)
                       ORDER BY day ASC""",
                    (f"-{days} days",),
                ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        log.error("get_mood_daily_averages failed: %s", e)
        return []


def get_activity_daily_counts(days: int = 30, user_id: int | None = None) -> list[dict]:
    """Per-day mood/journal counts for the last N days (optionally per user)."""
    try:
        days = max(1, min(365, int(days)))
        with _connect() as conn:
            if user_id is not None:
                mood_rows = conn.execute(
                    """SELECT date(created_at) AS day, COUNT(*) AS mood_count
                       FROM mood_logs
                       WHERE user_id = ? AND date(created_at) >= date('now', ?)
                       GROUP BY date(created_at)""",
                    (user_id, f"-{days} days"),
                ).fetchall()
                journal_rows = conn.execute(
                    """SELECT date(created_at) AS day, COUNT(*) AS journal_count
                       FROM journal_entries
                       WHERE user_id = ? AND date(created_at) >= date('now', ?)
                       GROUP BY date(created_at)""",
                    (user_id, f"-{days} days"),
                ).fetchall()
            else:
                mood_rows = conn.execute(
                    """SELECT date(created_at) AS day, COUNT(*) AS mood_count
                       FROM mood_logs
                       WHERE date(created_at) >= date('now', ?)
                       GROUP BY date(created_at)""",
                    (f"-{days} days",),
                ).fetchall()
                journal_rows = conn.execute(
                    """SELECT date(created_at) AS day, COUNT(*) AS journal_count
                       FROM journal_entries
                       WHERE date(created_at) >= date('now', ?)
                       GROUP BY date(created_at)""",
                    (f"-{days} days",),
                ).fetchall()
        mood_map = {r["day"]: r["mood_count"] for r in mood_rows}
        journal_map = {r["day"]: r["journal_count"] for r in journal_rows}
        all_days = sorted(set(mood_map) | set(journal_map))
        return [
            {
                "day": d,
                "mood_count": int(mood_map.get(d, 0)),
                "journal_count": int(journal_map.get(d, 0)),
            }
            for d in all_days
        ]
    except Exception as e:
        log.error("get_activity_daily_counts failed: %s", e)
        return []


def get_active_days(kind: str = "mood", days: int = 90, user_id: int | None = None) -> list[str]:
    """Distinct calendar days with activity, newest first. Optionally scoped to user."""
    try:
        days = max(1, min(365, int(days)))
        with _connect() as conn:
            if kind == "journal":
                if user_id is not None:
                    rows = conn.execute(
                        """SELECT DISTINCT date(created_at) AS day
                           FROM journal_entries
                           WHERE user_id = ? AND date(created_at) >= date('now', ?)
                           ORDER BY day DESC""",
                        (user_id, f"-{days} days"),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """SELECT DISTINCT date(created_at) AS day
                           FROM journal_entries
                           WHERE date(created_at) >= date('now', ?)
                           ORDER BY day DESC""",
                        (f"-{days} days",),
                    ).fetchall()
            elif kind == "either":
                if user_id is not None:
                    rows = conn.execute(
                        """SELECT day FROM (
                             SELECT date(created_at) AS day FROM mood_logs
                             WHERE user_id = ? AND date(created_at) >= date('now', ?)
                             UNION
                             SELECT date(created_at) AS day FROM journal_entries
                             WHERE user_id = ? AND date(created_at) >= date('now', ?)
                           )
                           ORDER BY day DESC""",
                        (user_id, f"-{days} days", user_id, f"-{days} days"),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """SELECT day FROM (
                             SELECT date(created_at) AS day FROM mood_logs
                             WHERE date(created_at) >= date('now', ?)
                             UNION
                             SELECT date(created_at) AS day FROM journal_entries
                             WHERE date(created_at) >= date('now', ?)
                           )
                           ORDER BY day DESC""",
                        (f"-{days} days", f"-{days} days"),
                    ).fetchall()
            else:
                if user_id is not None:
                    rows = conn.execute(
                        """SELECT DISTINCT date(created_at) AS day
                           FROM mood_logs
                           WHERE user_id = ? AND date(created_at) >= date('now', ?)
                           ORDER BY day DESC""",
                        (user_id, f"-{days} days"),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """SELECT DISTINCT date(created_at) AS day
                           FROM mood_logs
                           WHERE date(created_at) >= date('now', ?)
                           ORDER BY day DESC""",
                        (f"-{days} days",),
                    ).fetchall()
            return [r["day"] for r in rows if r["day"]]
    except Exception as e:
        log.error("get_active_days failed: %s", e)
        return []


def get_insights_totals(days: int = 30, user_id: int | None = None) -> dict:
    """Aggregate totals for the insights header cards (optionally per user)."""
    try:
        days = max(1, min(365, int(days)))
        with _connect() as conn:
            if user_id is not None:
                mood = conn.execute(
                    """SELECT COUNT(*) AS n, ROUND(AVG(rating), 2) AS avg_rating,
                              MIN(rating) AS min_rating, MAX(rating) AS max_rating
                       FROM mood_logs
                       WHERE user_id = ? AND date(created_at) >= date('now', ?)""",
                    (user_id, f"-{days} days"),
                ).fetchone()
                journals = conn.execute(
                    """SELECT COUNT(*) AS n FROM journal_entries
                       WHERE user_id = ? AND date(created_at) >= date('now', ?)""",
                    (user_id, f"-{days} days"),
                ).fetchone()
                sessions = conn.execute(
                    """SELECT COUNT(*) AS n FROM sessions
                       WHERE user_id = ? AND date(started_at) >= date('now', ?)""",
                    (user_id, f"-{days} days"),
                ).fetchone()
            else:
                mood = conn.execute(
                    """SELECT COUNT(*) AS n, ROUND(AVG(rating), 2) AS avg_rating,
                              MIN(rating) AS min_rating, MAX(rating) AS max_rating
                       FROM mood_logs
                       WHERE date(created_at) >= date('now', ?)""",
                    (f"-{days} days",),
                ).fetchone()
                journals = conn.execute(
                    """SELECT COUNT(*) AS n FROM journal_entries
                       WHERE date(created_at) >= date('now', ?)""",
                    (f"-{days} days",),
                ).fetchone()
                sessions = conn.execute(
                    """SELECT COUNT(*) AS n FROM sessions
                       WHERE date(started_at) >= date('now', ?)""",
                    (f"-{days} days",),
                ).fetchone()
        return {
            "mood_count": int(mood["n"] or 0) if mood else 0,
            "mood_avg": float(mood["avg_rating"]) if mood and mood["avg_rating"] is not None else None,
            "mood_min": int(mood["min_rating"]) if mood and mood["min_rating"] is not None else None,
            "mood_max": int(mood["max_rating"]) if mood and mood["max_rating"] is not None else None,
            "journal_count": int(journals["n"] or 0) if journals else 0,
            "session_count": int(sessions["n"] or 0) if sessions else 0,
            "days": days,
        }
    except Exception as e:
        log.error("get_insights_totals failed: %s", e)
        return {
            "mood_count": 0,
            "mood_avg": None,
            "mood_min": None,
            "mood_max": None,
            "journal_count": 0,
            "session_count": 0,
            "days": days,
        }
