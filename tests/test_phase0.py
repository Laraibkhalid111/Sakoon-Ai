"""Phase 0 + Phase 1 unit tests."""

from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sakoon.core.config import reload_settings, settings_public_dict  # noqa: E402
from sakoon.core.validation import validate_email, validate_name, validate_phone  # noqa: E402
from sakoon.services.chatbot import (  # noqa: E402
    _parse_json_response,
    _validate_and_fix,
    truncate_history,
)
from sakoon.services.safety import check_crisis  # noqa: E402


def test_crisis_english():
    assert check_crisis("I want to kill myself") is True
    assert check_crisis("I had a hard day at work") is False


def test_crisis_roman_urdu():
    assert check_crisis("main marna chahta hoon") is True


def test_crisis_urdu_script():
    assert check_crisis("میں خودکشی کے بارے میں سوچ رہا ہوں") is True


def test_html_escape_blocks_script():
    payload = '<script>alert("x")</script>'
    escaped = html.escape(payload)
    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped


def test_upsert_user_by_email(tmp_path, monkeypatch):
    import sakoon.db.database as db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    assert db.init_db() is True
    uid1 = db.upsert_user("Aisha", "aisha@example.com", None, "english")
    uid2 = db.upsert_user("Aisha K", "aisha@example.com", "+923001234567", "urdu")
    assert uid1 is not None and uid2 is not None
    assert uid1 == uid2


def test_truncate_history_keeps_tail():
    history = [{"role": "user", "content": str(i)} for i in range(40)]
    out = truncate_history(history, max_messages=10)
    assert len(out) == 10
    assert out[0]["content"] == "30"
    assert out[-1]["content"] == "39"
    assert len(history) == 40  # input not mutated


def test_parse_json_with_fences():
    raw = '```json\n{"reply_to_user": "hi", "conversation_stage": "check_in", "detected_language": "english", "extracted": {}, "suggested_coping_action": "none", "is_on_topic": true}\n```'
    data = _parse_json_response(raw)
    assert data is not None
    assert data["reply_to_user"] == "hi"


def test_validate_and_fix_clamps_mood():
    data = _validate_and_fix({
        "reply_to_user": "ok",
        "conversation_stage": "not-a-stage",
        "detected_language": "klingon",
        "suggested_coping_action": "dance",
        "is_on_topic": "yes",
        "extracted": {"mood_rating": 99, "symptoms": "anxiety"},
    })
    assert data["conversation_stage"] == "check_in"
    assert data["detected_language"] == "english"
    assert data["suggested_coping_action"] == "none"
    assert data["is_on_topic"] is True
    assert data["extracted"]["mood_rating"] == 10
    assert data["extracted"]["symptoms"] == []


def test_validation_helpers():
    assert validate_name("12")[0] is False
    assert validate_name("Laraib")[0] is True
    assert validate_email("bad")[0] is False
    assert validate_email("a@b.co")[0] is True
    assert validate_phone("123")[0] is False
    assert validate_phone("+923001234567")[0] is True


def test_settings_public_dict_hides_secrets(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "secret-key-should-not-leak")
    reload_settings()
    public = settings_public_dict()
    blob = str(public)
    assert "secret-key-should-not-leak" not in blob
    assert "has_groq" in public
