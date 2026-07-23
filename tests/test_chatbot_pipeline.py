"""Chatbot pipeline — API key hygiene + error classification."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_clean_secret_rejects_placeholders():
    from sakoon.core.config import _clean_secret

    assert _clean_secret(None) is None
    assert _clean_secret("") is None
    assert _clean_secret("  your_groq_api_key_here  ") is None
    assert _clean_secret('"changeme"') is None
    assert _clean_secret("gsk_live_not_a_real_key_but_format_ok") is not None


def test_stream_without_key_returns_auth_error(monkeypatch):
    import sakoon.core.config as cfg
    import sakoon.services.chatbot as bot

    monkeypatch.setattr(
        cfg,
        "get_settings",
        lambda: cfg.Settings(
            groq_api_key=None,
            email_address=None,
            email_app_password=None,
            smtp_host="smtp.gmail.com",
            smtp_port=465,
            chat_model="llama-3.3-70b-versatile",
            narrative_model="llama-3.1-8b-instant",
            whisper_model="whisper-large-v3-turbo",
            max_history_messages=24,
            log_level="INFO",
            encryption_key=None,
            rate_limit_chat_per_min=20,
            rate_limit_auth_per_min=10,
            backup_keep=14,
        ),
    )
    events = list(bot.stream_ai_response([{"role": "user", "content": "Hello"}]))
    assert len(events) == 1
    assert events[0]["type"] == "done"
    resp = events[0]["response"]
    assert resp.get("_error") is True
    assert resp.get("_error_kind") == "auth"
    assert "GROQ_API_KEY" in resp.get("reply_to_user", "")


def test_sample_intents_safety_and_policy():
    """Sanity: crisis gate + off-topic joke handling helpers stay wired."""
    from sakoon.services.reply_policy import choose_assistant_reply
    from sakoon.services.safety import check_crisis

    assert check_crisis("Hello") is False
    assert check_crisis("I feel anxious.") is False
    text, redirect = choose_assistant_reply(
        {"is_on_topic": False, "reply_to_user": "haha"},
        "english",
        valid_name=True,
        valid_email=True,
        valid_phone=True,
        redirect_copy="Let's keep this about how you're feeling.",
    )
    assert redirect is True
    assert "feeling" in text.lower()
