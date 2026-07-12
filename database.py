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
import logging
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "sakoon.db"

log = logging.getLogger(__name__)

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
    risk_level       TEXT DEFAULT 'low'
);

CREATE TABLE IF NOT EXISTS messages (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       INTEGER,
    role             TEXT,
    content          TEXT,
    input_mode       TEXT DEFAULT 'text',
    timestamp        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS symptom_snapshots (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id            INTEGER,
    mood_rating           INTEGER,
    symptoms_json         TEXT,
    triggers_json         TEXT,
    coping_suggestions_json TEXT,
    updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> bool:
    """
    Create all tables if they don't exist. Called once at app startup.
    Returns True on success, False on failure.
    """
    try:
        with _connect() as conn:
            conn.executescript(_SCHEMA)
        return True
    except Exception as e:
        log.error("init_db failed: %s", e)
        return False


# ── Users ─────────────────────────────────────────────────────────────────────

def upsert_user(name: str | None, email: str | None, phone: str | None,
                preferred_language: str = "english") -> int | None:
    """
    Insert a new user row and return the new id.
    Called once per session when contact info is first available.
    Returns the new user id, or None on failure.
    """
    try:
        with _connect() as conn:
            cur = conn.execute(
                "INSERT INTO users (name, email, phone, preferred_language) VALUES (?, ?, ?, ?)",
                (name, email, phone, preferred_language),
            )
            return cur.lastrowid
    except Exception as e:
        log.error("upsert_user failed: %s", e)
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
                   ended_at: str | None = None) -> bool:
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
    return update_session(
        session_id,
        ended_at=datetime.utcnow().isoformat(sep=" ", timespec="seconds"),
    )


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
            now = datetime.utcnow().isoformat(sep=" ", timespec="seconds")
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

def get_recent_sessions(limit: int = 5) -> list[dict]:
    """
    Return the most recent N sessions with their user name and primary concern.
    Used for the optional sidebar history list.
    """
    try:
        with _connect() as conn:
            rows = conn.execute(
                """SELECT s.id, u.name, s.primary_concern, s.started_at, s.risk_level
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
