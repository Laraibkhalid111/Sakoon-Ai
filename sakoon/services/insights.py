"""Insights computations — streaks, summaries, chart-ready series."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any


def _parse_day(value: str | date) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def compute_streak(active_days: list[str], today: date | None = None) -> dict[str, int]:
    """
    Compute current and best streaks from a list of YYYY-MM-DD day strings.
    Current streak allows today OR yesterday as the anchor (so timezone lag
    doesn't zero out a streak mid-evening).
    """
    today = today or date.today()
    days = sorted({d for d in (_parse_day(x) for x in active_days) if d}, reverse=True)
    if not days:
        return {"current": 0, "best": 0}

    # Best streak
    best = 1
    run = 1
    chronological = sorted(days)
    for i in range(1, len(chronological)):
        if chronological[i] - chronological[i - 1] == timedelta(days=1):
            run += 1
            best = max(best, run)
        else:
            run = 1

    # Current streak
    if days[0] not in (today, today - timedelta(days=1)):
        current = 0
    else:
        current = 1
        cursor = days[0]
        for d in days[1:]:
            if cursor - d == timedelta(days=1):
                current += 1
                cursor = d
            elif d == cursor:
                continue
            else:
                break

    return {"current": current, "best": best}


def build_weekly_summary(
    totals: dict[str, Any],
    mood_streak: dict[str, int],
    journal_streak: dict[str, int],
    checkin_streak: dict[str, int],
    lang: str = "english",
) -> str:
    """Rule-based weekly narrative from real aggregates (no LLM required)."""
    days = int(totals.get("days") or 7)
    mood_n = int(totals.get("mood_count") or 0)
    journal_n = int(totals.get("journal_count") or 0)
    avg = totals.get("mood_avg")
    sessions = int(totals.get("session_count") or 0)

    if lang == "urdu":
        if mood_n == 0 and journal_n == 0:
            return (
                f"گزشتہ {days} دنوں میں ابھی کوئی مزاج یا جرنل محفوظ نہیں۔ "
                "آج ایک چھوٹا سا چیک اِن شروع کریں — ایک نمبر بھی کافی ہے۔"
            )
        avg_txt = f"{avg:.1f}" if avg is not None else "—"
        return (
            f"گزشتہ {days} دنوں میں آپ نے {mood_n} مزاج چیک اِن اور {journal_n} جرنل اندراجات محفوظ کیے۔ "
            f"اوسط مزاج {avg_txt}/10 رہا۔ "
            f"موجودہ چیک اِن سلسلہ {checkin_streak.get('current', 0)} دن ہے "
            f"(بہترین {checkin_streak.get('best', 0)})۔ "
            f"گفتگو کی نشستیں: {sessions}۔"
        )
    if lang == "roman_urdu":
        if mood_n == 0 and journal_n == 0:
            return (
                f"Pichle {days} dinon mein abhi koi mood ya journal save nahi hua. "
                "Aaj chhota sa check-in shuru karein — ek number bhi kaafi hai."
            )
        avg_txt = f"{avg:.1f}" if avg is not None else "—"
        return (
            f"Pichle {days} dinon mein aapne {mood_n} mood check-ins aur {journal_n} journal entries save kiye. "
            f"Average mood {avg_txt}/10 raha. "
            f"Current check-in streak {checkin_streak.get('current', 0)} din hai "
            f"(best {checkin_streak.get('best', 0)}). "
            f"Chat sessions: {sessions}."
        )

    if mood_n == 0 and journal_n == 0:
        return (
            f"Over the last {days} days, nothing is logged yet. "
            "Start with one small check-in today — even a single mood number helps."
        )
    avg_txt = f"{avg:.1f}" if avg is not None else "—"
    return (
        f"Over the last {days} days you logged {mood_n} mood check-ins and {journal_n} journal entries. "
        f"Average mood was {avg_txt}/10. "
        f"Your check-in streak is {checkin_streak.get('current', 0)} day(s) "
        f"(best {checkin_streak.get('best', 0)}). "
        f"Chat sessions started: {sessions}."
    )


def insights_ui_copy(lang: str) -> dict[str, str]:
    if lang == "urdu":
        return {
            "nav": "بصیرت",
            "title": "آپ کی بصیرت",
            "subtitle": "مزاج کے رجحانات، سلسلے، اور ہفتہ وار خلاصہ — حقیقی ڈیٹا سے۔",
            "range_7": "۷ دن",
            "range_30": "۳۰ دن",
            "range_90": "۹۰ دن",
            "stat_mood": "مزاج چیک اِن",
            "stat_avg": "اوسط مزاج",
            "stat_journal": "جرنل",
            "stat_sessions": "نشستیں",
            "streak_mood": "مزاج سلسلہ",
            "streak_journal": "جرنل سلسلہ",
            "streak_checkin": "چیک اِن سلسلہ",
            "streak_best": "بہترین",
            "streak_days": "دن",
            "chart_mood": "روزانہ اوسط مزاج",
            "chart_activity": "روزانہ سرگرمی",
            "summary": "خلاصہ",
            "empty": "ابھی چارٹ کے لیے کافی ڈیٹا نہیں۔ پہلے فلاحی کمرے میں مزاج یا جرنل محفوظ کریں۔",
            "mood_series": "مزاج",
            "activity_mood": "مزاج اندراجات",
            "activity_journal": "جرنل اندراجات",
        }
    if lang == "roman_urdu":
        return {
            "nav": "Insights",
            "title": "Aapki insights",
            "subtitle": "Mood trends, streaks, aur weekly summary — asli data se.",
            "range_7": "7 din",
            "range_30": "30 din",
            "range_90": "90 din",
            "stat_mood": "Mood check-ins",
            "stat_avg": "Average mood",
            "stat_journal": "Journal",
            "stat_sessions": "Sessions",
            "streak_mood": "Mood streak",
            "streak_journal": "Journal streak",
            "streak_checkin": "Check-in streak",
            "streak_best": "Best",
            "streak_days": "din",
            "chart_mood": "Daily average mood",
            "chart_activity": "Daily activity",
            "summary": "Summary",
            "empty": "Charts ke liye abhi data kam hai. Pehle Wellness mein mood ya journal save karein.",
            "mood_series": "Mood",
            "activity_mood": "Mood logs",
            "activity_journal": "Journal entries",
        }
    return {
        "nav": "Insights",
        "title": "Your insights",
        "subtitle": "Mood trends, streaks, and a weekly summary — from your real check-ins.",
        "range_7": "7 days",
        "range_30": "30 days",
        "range_90": "90 days",
        "stat_mood": "Mood check-ins",
        "stat_avg": "Average mood",
        "stat_journal": "Journal entries",
        "stat_sessions": "Sessions",
        "streak_mood": "Mood streak",
        "streak_journal": "Journal streak",
        "streak_checkin": "Check-in streak",
        "streak_best": "Best",
        "streak_days": "days",
        "chart_mood": "Daily average mood",
        "chart_activity": "Daily activity",
        "summary": "Summary",
        "empty": "Not enough data for charts yet. Save a mood or journal entry in Wellness first.",
        "mood_series": "Mood",
        "activity_mood": "Mood logs",
        "activity_journal": "Journal entries",
    }


def collect_insights(days: int, lang: str = "english", user_id: int | None = None) -> dict[str, Any]:
    """Assemble everything the insights dashboard needs (scoped to user when set)."""
    from sakoon.db import (
        get_active_days,
        get_activity_daily_counts,
        get_insights_totals,
        get_mood_daily_averages,
    )

    totals = get_insights_totals(days=days, user_id=user_id)
    mood_days = get_active_days("mood", days=max(days, 90), user_id=user_id)
    journal_days = get_active_days("journal", days=max(days, 90), user_id=user_id)
    either_days = get_active_days("either", days=max(days, 90), user_id=user_id)

    mood_streak = compute_streak(mood_days)
    journal_streak = compute_streak(journal_days)
    checkin_streak = compute_streak(either_days)

    return {
        "days": days,
        "totals": totals,
        "mood_series": get_mood_daily_averages(days=days, user_id=user_id),
        "activity": get_activity_daily_counts(days=days, user_id=user_id),
        "mood_streak": mood_streak,
        "journal_streak": journal_streak,
        "checkin_streak": checkin_streak,
        "summary": build_weekly_summary(
            totals, mood_streak, journal_streak, checkin_streak, lang=lang
        ),
    }
