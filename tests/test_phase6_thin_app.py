"""P6 — reply policy + thin entry wiring."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sakoon.core.validation import validate_email, validate_name, validate_phone  # noqa: E402
from sakoon.services.reply_policy import (  # noqa: E402
    apply_language_from_response,
    avatar_initials,
    choose_assistant_reply,
    merge_extracted_fields,
    rate_limit_message,
)
from sakoon.services.safety import check_crisis  # noqa: E402


def test_apply_language_from_response():
    assert apply_language_from_response("urdu", "Auto") == "urdu"
    assert apply_language_from_response("urdu", "English") == "english"
    assert apply_language_from_response("english", "اردو") == "urdu"


def test_choose_assistant_reply_off_topic_and_validation():
    redirect = "Please stay on wellness topics."
    text, is_redirect = choose_assistant_reply(
        {"is_on_topic": False, "reply_to_user": "ignored"},
        "english",
        valid_name=True,
        valid_email=True,
        valid_phone=True,
        redirect_copy=redirect,
    )
    assert text == redirect and is_redirect is True

    text, is_redirect = choose_assistant_reply(
        {"is_on_topic": True, "reply_to_user": "Hello"},
        "english",
        valid_name=False,
        valid_email=True,
        valid_phone=True,
        redirect_copy=redirect,
    )
    assert "name" in text.lower() and is_redirect is False

    text, is_redirect = choose_assistant_reply(
        {"is_on_topic": True, "reply_to_user": "Hello friend"},
        "english",
        valid_name=True,
        valid_email=True,
        valid_phone=True,
        redirect_copy=redirect,
    )
    assert text == "Hello friend" and is_redirect is False


def test_merge_extracted_fields_contact_and_lists():
    profile = {"symptoms": ["tired"], "risk_flags": [], "coping_suggestions": []}
    profile, vn, ve, vp, mood = merge_extracted_fields(
        profile,
        {
            "name": "Ayesha",
            "email": "a@example.com",
            "mood_rating": 6,
            "symptoms": ["anxious"],
            "primary_concern": "sleep",
        },
        validate_name=validate_name,
        validate_email=validate_email,
        validate_phone=validate_phone,
    )
    assert vn and ve and vp
    assert profile["name"] == "Ayesha"
    assert profile["email"] == "a@example.com"
    assert profile["primary_concern"] == "sleep"
    assert profile["symptoms"] == ["tired", "anxious"]
    assert mood == 6


def test_avatar_and_rate_limit_copy():
    assert avatar_initials("Laraib Khalid") == "LK"
    assert avatar_initials("Sam") == "SA"
    assert "seconds" in rate_limit_message("english", 3)
    assert "سیکنڈ" in rate_limit_message("urdu", 3)


def test_crisis_still_gates_before_llm_path():
    assert check_crisis("I want to kill myself") is True
    assert check_crisis("I had a stressful day at work") is False


def test_app_entrypoint_is_thin():
    app_path = ROOT / "app.py"
    lines = app_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 80
    src = app_path.read_text(encoding="utf-8")
    assert "render_chat_view" in src
    assert "render_sidebar" in src
    assert "def _process_ai_turn" not in src
