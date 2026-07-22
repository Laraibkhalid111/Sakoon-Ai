"""P4 — conversation rename / delete / export (local)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_rename_delete_export_session(tmp_path, monkeypatch):
    import sakoon.db.database as db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "conv.db")
    db._SCHEMA_READY_FOR = None
    assert db.init_db() is True

    uid = db.get_or_create_local_user()
    sid = db.create_session(uid)
    assert sid is not None
    db.log_message(sid, "user", "I feel anxious today")
    db.log_message(sid, "assistant", "I'm here with you.")

    assert db.ensure_session_title_from_text(sid, "I feel anxious today") is True
    rows = db.get_recent_sessions(limit=5, user_id=uid)
    assert rows and "anxious" in (rows[0].get("title") or "").lower()

    # Second ensure should not overwrite
    assert db.ensure_session_title_from_text(sid, "Different text") is False

    assert db.rename_session(sid, uid, "Morning check-in") is True
    rows = db.get_recent_sessions(limit=5, user_id=uid)
    assert rows[0]["title"] == "Morning check-in"
    assert db.session_label(rows[0]) == "Morning check-in"

    md = db.export_session_markdown(sid, uid)
    assert md is not None
    assert "# Morning check-in" in md
    assert "I feel anxious today" in md
    assert "I'm here with you." in md
    assert "### You" in md
    assert "### Sakoon" in md

    # Wrong user cannot export/delete
    assert db.export_session_markdown(sid, uid + 999) is None
    assert db.delete_session(sid, uid + 999) is False

    mood_id = db.add_mood_log(rating=6, note="ok", session_id=sid, user_id=uid)
    assert mood_id is not None

    assert db.delete_session(sid, uid) is True
    assert db.get_recent_sessions(limit=5, user_id=uid) == []
    assert db.get_messages(sid) == []
    # Mood survives, detached from session
    moods = db.get_mood_logs(limit=5, user_id=uid)
    assert len(moods) == 1
    assert moods[0].get("session_id") is None


def test_session_title_migration(tmp_path, monkeypatch):
    import sqlite3
    import sakoon.db.database as db

    path = tmp_path / "old.db"
    monkeypatch.setattr(db, "DB_PATH", path)
    db._SCHEMA_READY_FOR = None

    # Simulate pre-title schema
    conn = sqlite3.connect(str(path))
    conn.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT,
            preferred_language TEXT DEFAULT 'english',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            primary_concern TEXT,
            risk_level TEXT DEFAULT 'low'
        );
        """
    )
    conn.close()

    assert db.init_db() is True
    cols = set()
    with db._connect() as c:
        cols = {row[1] for row in c.execute("PRAGMA table_info(sessions)").fetchall()}
    assert "title" in cols
