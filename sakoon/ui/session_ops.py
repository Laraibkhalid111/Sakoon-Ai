"""Session history helpers for sidebar load / new chat / auth bootstrap."""

from __future__ import annotations

from typing import Any

import streamlit as st

from sakoon.db import create_session, get_messages, get_snapshot, session_belongs_to_user
from sakoon.services.prompts import WELCOME_MESSAGE
from sakoon.ui.components import timestamp_now

_CHAT_KEYS = (
    "messages", "groq_history", "profile", "stage", "lang", "detected_lang",
    "mood", "crisis_triggered", "show_error", "db_error", "thinking",
    "report_bytes", "last_session_data", "last_narrative",
    "db_session_id", "whisper_error", "pending_voice_text",
    "voice_recorder_key", "pending_ai_turn", "session_closed",
    "active_coping", "coping_step", "coping_completed",
    "journal_notes", "journal_draft", "history_readonly", "main_view",
)


def _inject_welcome() -> None:
    w = WELCOME_MESSAGE
    st.session_state.messages = [{
        "role": "assistant",
        "content": w["reply_to_user"],
        "is_redirect": False,
        "is_voice": False,
        "ts": timestamp_now(),
    }]
    st.session_state.groq_history = [{
        "role": "assistant",
        "content": w["reply_to_user"],
    }]


def start_new_chat() -> None:
    """Reset chat state and open a fresh DB session for the signed-in user."""
    prev_voice_key = int(st.session_state.get("voice_recorder_key", 0) or 0)
    theme = st.session_state.get("theme", "light")
    user_id = st.session_state.get("db_user_id")
    username = st.session_state.get("auth_username")
    authenticated = bool(st.session_state.get("authenticated"))

    for key in _CHAT_KEYS:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.theme = theme
    st.session_state.authenticated = authenticated
    st.session_state.db_user_id = user_id
    st.session_state.auth_username = username
    st.session_state.messages = []
    st.session_state.groq_history = []
    st.session_state.profile = {**WELCOME_MESSAGE["extracted"], "coping_suggestions": []}
    st.session_state.stage = "greeting"
    st.session_state.lang = "english"
    st.session_state.detected_lang = "english"
    st.session_state.mood = None
    st.session_state.crisis_triggered = False
    st.session_state.show_error = None
    st.session_state.db_error = False
    st.session_state.thinking = False
    st.session_state.report_bytes = None
    st.session_state.last_session_data = None
    st.session_state.last_narrative = None
    st.session_state.db_session_id = None
    st.session_state.whisper_error = False
    st.session_state.pending_voice_text = None
    st.session_state.voice_recorder_key = prev_voice_key + 1
    st.session_state.pending_ai_turn = None
    st.session_state.session_closed = False
    st.session_state.active_coping = None
    st.session_state.coping_step = 0
    st.session_state.coping_completed = False
    st.session_state.journal_notes = []
    st.session_state.journal_draft = ""
    st.session_state.history_readonly = False
    st.session_state.main_view = "chat"

    _inject_welcome()

    sid = create_session(user_id=user_id)
    if sid:
        st.session_state.db_session_id = sid


def bootstrap_authenticated_session(user: dict[str, Any]) -> None:
    """Called after successful login/register — bind identity and start a chat."""
    st.session_state.authenticated = True
    st.session_state.db_user_id = int(user["id"])
    st.session_state.auth_username = user.get("username")
    if user.get("preferred_language"):
        st.session_state.lang = user["preferred_language"]
        st.session_state.detected_lang = user["preferred_language"]
    start_new_chat()


def logout_user() -> None:
    """Clear auth + chat state; keep theme preference."""
    theme = st.session_state.get("theme", "light")
    for key in list(st.session_state.keys()):
        if key in ("theme", "lang_override_select", "theme_toggle"):
            continue
        del st.session_state[key]
    st.session_state.theme = theme
    st.session_state.authenticated = False
    st.session_state.db_user_id = None
    st.session_state.auth_username = None


def load_past_session(session_id: int) -> bool:
    """Load messages from a past session owned by the current user."""
    uid = st.session_state.get("db_user_id")
    if uid is None or not session_belongs_to_user(session_id, int(uid)):
        return False

    rows = get_messages(session_id)
    if not rows:
        return False

    messages = []
    groq_history = []
    for row in rows:
        role = row.get("role") or "assistant"
        content = row.get("content") or ""
        mode = row.get("input_mode") or "text"
        ts_raw = row.get("timestamp") or ""
        ts = str(ts_raw)[-8:] if ts_raw else timestamp_now()
        messages.append({
            "role": role,
            "content": content,
            "is_redirect": False,
            "is_voice": mode == "voice",
            "ts": ts,
        })
        if role in ("user", "assistant"):
            groq_history.append({"role": role, "content": content})

    st.session_state.messages = messages
    st.session_state.groq_history = groq_history
    st.session_state.db_session_id = session_id
    st.session_state.session_closed = False
    st.session_state.pending_ai_turn = None
    st.session_state.thinking = False
    st.session_state.report_bytes = None
    st.session_state.active_coping = None
    st.session_state.history_readonly = False

    snap = get_snapshot(session_id)
    if snap:
        profile = st.session_state.setdefault("profile", {})
        if snap.get("mood_rating") is not None:
            profile["mood_rating"] = snap["mood_rating"]
            st.session_state.mood = snap["mood_rating"]
        profile["symptoms"] = snap.get("symptoms_json") or []
        profile["possible_triggers"] = snap.get("triggers_json") or []
        profile["coping_suggestions"] = snap.get("coping_suggestions_json") or []
        st.session_state.profile = profile

    return True
