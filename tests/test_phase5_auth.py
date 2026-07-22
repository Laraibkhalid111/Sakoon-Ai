"""Phase 5 — multi-user auth, data isolation, journal encryption."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sakoon.services.auth import (  # noqa: E402
    authenticate,
    hash_password,
    register_user,
    validate_password,
    validate_username,
    verify_password,
)


def test_validate_username_and_password():
    assert validate_username("ab")[0] is False
    assert validate_username("good_user")[0] is True
    assert validate_password("short")[0] is False
    assert validate_password("longenough")[0] is True


def test_bcrypt_roundtrip():
    h = hash_password("secretpass99")
    assert h != "secretpass99"
    assert verify_password("secretpass99", h) is True
    assert verify_password("wrong", h) is False


def test_register_and_authenticate(tmp_path, monkeypatch):
    import sakoon.db.database as db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "auth.db")
    assert db.init_db() is True

    ok, msg, uid = register_user("alice_1", "password123", name="Alice")
    assert ok is True
    assert uid is not None

    ok2, _, uid2 = register_user("alice_1", "password123")
    assert ok2 is False

    ok3, _, user = authenticate("alice_1", "password123")
    assert ok3 is True
    assert user["id"] == uid
    assert "password_hash" not in user

    bad, _, user_bad = authenticate("alice_1", "wrongpassword")
    assert bad is False
    assert user_bad is None


def test_session_and_data_isolation(tmp_path, monkeypatch):
    import sakoon.db.database as db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "iso.db")
    assert db.init_db() is True

    _, _, uid_a = register_user("user_a", "password123")
    _, _, uid_b = register_user("user_b", "password123")
    assert uid_a and uid_b

    sid_a = db.create_session(uid_a)
    sid_b = db.create_session(uid_b)
    assert sid_a and sid_b
    assert db.session_belongs_to_user(sid_a, uid_a) is True
    assert db.session_belongs_to_user(sid_a, uid_b) is False

    db.add_mood_log(7, note="a", user_id=uid_a, session_id=sid_a)
    db.add_mood_log(3, note="b", user_id=uid_b, session_id=sid_b)
    db.add_journal_entry("private A", user_id=uid_a, session_id=sid_a)
    db.add_journal_entry("private B", user_id=uid_b, session_id=sid_b)

    moods_a = db.get_mood_logs(user_id=uid_a)
    moods_b = db.get_mood_logs(user_id=uid_b)
    assert len(moods_a) == 1 and moods_a[0]["note"] == "a"
    assert len(moods_b) == 1 and moods_b[0]["note"] == "b"

    journals_a = db.get_journal_entries(user_id=uid_a)
    journals_b = db.get_journal_entries(user_id=uid_b)
    assert journals_a[0]["body"] == "private A"
    assert journals_b[0]["body"] == "private B"

    recent_a = db.get_recent_sessions(limit=10, user_id=uid_a)
    assert all(r["id"] == sid_a for r in recent_a)

    totals_a = db.get_insights_totals(days=30, user_id=uid_a)
    totals_b = db.get_insights_totals(days=30, user_id=uid_b)
    assert totals_a["mood_count"] == 1
    assert totals_b["mood_count"] == 1
    assert totals_a["journal_count"] == 1


def test_journal_encryption_when_key_set(tmp_path, monkeypatch):
    from cryptography.fernet import Fernet

    import sakoon.db.database as db
    from sakoon.core.config import reload_settings
    from sakoon.core.crypto import decrypt_text, encrypt_text

    key = Fernet.generate_key().decode("utf-8")
    monkeypatch.setenv("ENCRYPTION_KEY", key)
    reload_settings()

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "enc.db")
    assert db.init_db() is True
    _, _, uid = register_user("enc_user", "password123")
    sid = db.create_session(uid)

    cipher = encrypt_text("my secret note")
    assert cipher.startswith("enc:v1:")
    assert decrypt_text(cipher) == "my secret note"

    jid = db.add_journal_entry("my secret note", user_id=uid, session_id=sid)
    assert jid is not None

    with db._connect() as conn:
        raw = conn.execute(
            "SELECT body FROM journal_entries WHERE id = ?", (jid,)
        ).fetchone()["body"]
    assert raw.startswith("enc:v1:")
    assert "my secret note" not in raw

    rows = db.get_journal_entries(user_id=uid)
    assert rows[0]["body"] == "my secret note"
