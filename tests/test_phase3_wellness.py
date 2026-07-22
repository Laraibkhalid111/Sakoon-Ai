"""Phase 3 wellness — mood/journal DB + affirmations/resources content."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sakoon.services.wellness import (  # noqa: E402
    affirmation_for_today,
    emergency_resources,
    list_affirmations,
    mood_label,
)


def test_affirmation_rotates_deterministically():
    a = affirmation_for_today("english")
    b = affirmation_for_today("english")
    assert a == b
    assert a in list_affirmations("english")
    assert affirmation_for_today("urdu") in list_affirmations("urdu")


def test_emergency_resources_have_helpline():
    en = emergency_resources("english")
    assert any("0311" in r["detail"] for r in en)
    ur = emergency_resources("urdu")
    assert len(ur) >= 3
    assert all("name" in r and "when" in r for r in ur)


def test_mood_label_bounds():
    assert "hard" in mood_label(1, "english").lower() or "Hard" in mood_label(1, "english")
    assert mood_label(10, "english")


def test_mood_and_journal_persistence(tmp_path, monkeypatch):
    import sakoon.db.database as db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "wellness.db")
    assert db.init_db() is True
    sid = db.create_session(None)
    mid = db.add_mood_log(7, note="ok day", session_id=sid, source="manual")
    jid = db.add_journal_entry("I felt lighter after a walk.", prompt="prompt", session_id=sid)
    assert mid and jid
    moods = db.get_mood_logs(limit=5)
    journals = db.get_journal_entries(limit=5)
    assert moods[0]["rating"] == 7
    assert "walk" in journals[0]["body"]
