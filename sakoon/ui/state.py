"""Session state bootstrap for the Streamlit entrypoint."""

from __future__ import annotations

import streamlit as st

from sakoon.core.health import check_health
from sakoon.core.metrics import emit
from sakoon.db import create_session, init_db
from sakoon.services.prompts import WELCOME_MESSAGE
from sakoon.ui.components import timestamp_now
from sakoon.ui.session_ops import ensure_local_identity


_STATE_DEFAULTS = {
    "messages": [],
    "groq_history": [],
    "profile": None,  # filled in init_session_state
    "stage": "greeting",
    "lang": "english",
    "detected_lang": "english",
    "mood": None,
    "crisis_triggered": False,
    "show_error": None,
    "db_error": False,
    "thinking": False,
    "report_bytes": None,
    "last_session_data": None,
    "last_narrative": None,
    "db_session_id": None,
    "db_user_id": None,
    "whisper_error": False,
    "pending_voice_text": None,
    "voice_recorder_key": 0,
    "pending_ai_turn": None,
    "session_closed": False,
    "theme": "light",
    "active_coping": None,
    "coping_step": 0,
    "coping_completed": False,
    "journal_notes": [],
    "journal_draft": "",
    "history_readonly": False,
    "main_view": "chat",
    "local_mode": True,
    "cancel_generation": False,
    "voice_draft": None,
    "auto_scroll": False,
}


def init_session_state() -> None:
    """Ensure all session keys exist and inject the welcome turn once."""
    defaults = dict(_STATE_DEFAULTS)
    defaults["profile"] = {**WELCOME_MESSAGE["extracted"]}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state.messages:
        welcome = WELCOME_MESSAGE["reply_to_user"]
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome,
            "is_redirect": False,
            "is_voice": False,
            "ts": timestamp_now(),
        })
        st.session_state.groq_history.append({
            "role": "assistant",
            "content": welcome,
        })


def resolve_language_override() -> None:
    """Apply sidebar language override (or fall back to detected language)."""
    override = st.session_state.get("lang_override_select", "Auto")
    if override == "English":
        st.session_state.lang = "english"
    elif override == "اردو":
        st.session_state.lang = "urdu"
    else:
        st.session_state.lang = st.session_state.get("detected_lang", "english")


def bootstrap_local_db() -> bool:
    """
    Init SQLite, bind local device user, ensure an open session.
    Returns True when the database is usable.
    """
    ok = init_db()
    if ok and not st.session_state.get("_health_logged"):
        health = check_health()
        emit(
            "app_ready",
            ok=health.get("ok"),
            has_groq=health.get("settings", {}).get("has_groq"),
        )
        st.session_state._health_logged = True

    if ok:
        ensure_local_identity(preferred_language=st.session_state.get("lang", "english"))

    if ok and st.session_state.db_session_id is None:
        sid = create_session(user_id=st.session_state.get("db_user_id"))
        if sid:
            st.session_state.db_session_id = sid
    return ok
