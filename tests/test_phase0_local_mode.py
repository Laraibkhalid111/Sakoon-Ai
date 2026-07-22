"""P0 — local mode (no auth gate); local device user."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_get_or_create_local_user_stable(tmp_path, monkeypatch):
    import sakoon.db.database as db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "local.db")
    assert db.init_db() is True

    uid1 = db.get_or_create_local_user()
    uid2 = db.get_or_create_local_user()
    assert uid1 is not None
    assert uid1 == uid2

    # Contact email update must not create a second local identity
    assert db.update_user(uid1, email="person@example.com", name="Ayesha") is True
    uid3 = db.get_or_create_local_user()
    assert uid3 == uid1

    row = db.get_user_by_id(uid1)
    assert row is not None
    assert row["name"] == "Ayesha"


def test_local_sessions_scoped(tmp_path, monkeypatch):
    import sakoon.db.database as db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "local2.db")
    assert db.init_db() is True
    uid = db.get_or_create_local_user()
    sid = db.create_session(uid)
    assert sid is not None
    assert db.session_belongs_to_user(sid, uid) is True
    recent = db.get_recent_sessions(limit=5, user_id=uid)
    assert any(r["id"] == sid for r in recent)


def test_delete_last_assistant_message(tmp_path, monkeypatch):
    import sakoon.db.database as db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "regen.db")
    assert db.init_db() is True
    sid = db.create_session(db.get_or_create_local_user())
    db.log_message(sid, "user", "hello")
    db.log_message(sid, "assistant", "first")
    db.log_message(sid, "assistant", "second")
    assert db.delete_last_assistant_message(sid) is True
    rows = db.get_messages(sid)
    assert len(rows) == 2
    assert rows[-1]["content"] == "first"
    assert rows[-1]["role"] == "assistant"


def test_init_db_skips_repeat_work(tmp_path, monkeypatch):
    import sakoon.db.database as db

    path = tmp_path / "once.db"
    monkeypatch.setattr(db, "DB_PATH", path)
    db._SCHEMA_READY_FOR = None
    assert db.init_db() is True
    assert db._SCHEMA_READY_FOR == path
    # Second call should no-op successfully without error
    assert db.init_db() is True
