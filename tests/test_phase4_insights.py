"""Phase 4 insights — streaks + analytics queries."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sakoon.services.insights import build_weekly_summary, compute_streak  # noqa: E402


def test_compute_streak_current_and_best():
    today = date(2026, 7, 22)
    days = [
        "2026-07-22",
        "2026-07-21",
        "2026-07-20",
        "2026-07-18",
        "2026-07-17",
    ]
    result = compute_streak(days, today=today)
    assert result["current"] == 3
    assert result["best"] == 3


def test_compute_streak_allows_yesterday_anchor():
    today = date(2026, 7, 22)
    days = ["2026-07-21", "2026-07-20"]
    result = compute_streak(days, today=today)
    assert result["current"] == 2


def test_compute_streak_empty():
    assert compute_streak([]) == {"current": 0, "best": 0}


def test_weekly_summary_empty_english():
    text = build_weekly_summary(
        {"days": 7, "mood_count": 0, "journal_count": 0, "mood_avg": None, "session_count": 0},
        {"current": 0, "best": 0},
        {"current": 0, "best": 0},
        {"current": 0, "best": 0},
        lang="english",
    )
    assert "nothing is logged" in text.lower() or "Nothing" in text


def test_insights_db_aggregates(tmp_path, monkeypatch):
    import sakoon.db.database as db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "insights.db")
    assert db.init_db() is True
    sid = db.create_session(None)
    # Backdate via raw SQL for multi-day series
    with db._connect() as conn:
        conn.execute(
            "INSERT INTO mood_logs (session_id, rating, source, created_at) VALUES (?, ?, ?, ?)",
            (sid, 6, "manual", "2026-07-20 10:00:00"),
        )
        conn.execute(
            "INSERT INTO mood_logs (session_id, rating, source, created_at) VALUES (?, ?, ?, ?)",
            (sid, 8, "manual", "2026-07-21 10:00:00"),
        )
        conn.execute(
            "INSERT INTO journal_entries (session_id, body, created_at) VALUES (?, ?, ?)",
            (sid, "felt okay", "2026-07-21 11:00:00"),
        )

    series = db.get_mood_daily_averages(days=30)
    assert len(series) >= 2
    activity = db.get_activity_daily_counts(days=30)
    assert any(r["journal_count"] >= 1 for r in activity)
    totals = db.get_insights_totals(days=30)
    assert totals["mood_count"] >= 2
    assert totals["journal_count"] >= 1
    assert db.get_active_days("either", days=30)
