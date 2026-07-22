"""P5 — stop generation helpers + chrome strings."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_cancel_ai_turn_clears_pending(monkeypatch):
    import streamlit as st
    from sakoon.ui.session_ops import cancel_ai_turn
    from types import SimpleNamespace

    state = SimpleNamespace(
        cancel_generation=False,
        pending_ai_turn={"raw": "hi", "is_voice": False},
        thinking=True,
        regenerate_requested=True,
        messages=[
            {"role": "assistant", "content": "hello"},
            {"role": "user", "content": "hi"},
        ],
        groq_history=[
            {"role": "assistant", "content": "hello"},
            {"role": "user", "content": "hi"},
        ],
    )
    monkeypatch.setattr(st, "session_state", state)

    cancel_ai_turn(keep_user_message=True)
    assert state.pending_ai_turn is None
    assert state.thinking is False
    assert state.cancel_generation is True
    assert state.messages[-1]["role"] == "user"

    cancel_ai_turn(keep_user_message=False)
    assert state.messages[-1]["role"] == "assistant"
    assert state.groq_history[-1]["role"] == "assistant"


def test_chrome_has_stop_and_voice_keys():
    from sakoon.ui.shell import chrome_copy

    for lang in ("english", "urdu", "roman_urdu"):
        ui = chrome_copy(lang)
        for key in ("stop", "stop_help", "voice_send", "voice_discard", "voice_badge"):
            assert ui.get(key)
