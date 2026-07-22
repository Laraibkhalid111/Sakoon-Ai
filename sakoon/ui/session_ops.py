"""Session history helpers — local device profile (no login)."""

from __future__ import annotations

import streamlit as st

from sakoon.db import (
    create_session,
    delete_session,
    export_session_markdown,
    get_messages,
    get_or_create_local_user,
    get_snapshot,
    rename_session,
    session_belongs_to_user,
    session_label,
)
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
    "cancel_generation", "voice_draft",
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


def cancel_ai_turn(*, keep_user_message: bool = True) -> None:
    """
    Cancel a queued or in-flight generation.
    Keeps the last user message by default (ChatGPT-style stop).
    """
    st.session_state.cancel_generation = True
    st.session_state.pending_ai_turn = None
    st.session_state.thinking = False
    st.session_state.regenerate_requested = False
    if keep_user_message:
        return
    msgs = getattr(st.session_state, "messages", None) or []
    if msgs and msgs[-1].get("role") == "user":
        msgs.pop()
    hist = getattr(st.session_state, "groq_history", None) or []
    if hist and hist[-1].get("role") == "user":
        hist.pop()


def generation_was_cancelled() -> bool:
    """Consume cancel flag; True if caller should abort."""
    if st.session_state.pop("cancel_generation", False):
        st.session_state.pending_ai_turn = None
        st.session_state.thinking = False
        return True
    return False


def ensure_local_identity(preferred_language: str = "english") -> int | None:
    """
    Bind Streamlit session to the local device user (no accounts).
    Returns user id or None if DB unavailable.
    """
    if st.session_state.get("db_user_id"):
        return int(st.session_state.db_user_id)

    uid = get_or_create_local_user(preferred_language=preferred_language)
    if uid is None:
        return None
    st.session_state.db_user_id = int(uid)
    st.session_state.local_mode = True
    return int(uid)


def start_new_chat() -> None:
    """Reset chat state and open a fresh DB session for the local user."""
    prev_voice_key = int(st.session_state.get("voice_recorder_key", 0) or 0)
    theme = st.session_state.get("theme", "light")
    user_id = st.session_state.get("db_user_id")
    # Preserve language preference across new chats
    lang = st.session_state.get("lang") or "english"
    detected = st.session_state.get("detected_lang") or lang

    for key in _CHAT_KEYS:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.theme = theme
    st.session_state.db_user_id = user_id
    st.session_state.local_mode = True
    st.session_state.messages = []
    st.session_state.groq_history = []
    st.session_state.profile = {**WELCOME_MESSAGE["extracted"], "coping_suggestions": []}
    st.session_state.stage = "greeting"
    st.session_state.lang = lang
    st.session_state.detected_lang = detected
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
    st.session_state.cancel_generation = False
    st.session_state.voice_draft = None

    _inject_welcome()

    sid = create_session(user_id=user_id)
    if sid:
        st.session_state.db_session_id = sid


def load_past_session(session_id: int) -> bool:
    """Load messages from a past session owned by the local user."""
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


def render_conversation_history(
    recent: list,
    ui: dict,
    *,
    on_mutate=None,
) -> None:
    """
    ChatGPT-lite history: open, rename, export Markdown, delete (local only).
    `on_mutate` is called after rename/delete so the caller can clear caches.
    """
    if not recent:
        st.caption(ui.get("empty_history", "No past conversations yet."))
        return

    current_id = st.session_state.db_session_id
    uid = st.session_state.get("db_user_id")

    for row in recent:
        sid = int(row.get("id"))
        label = session_label(row)
        started = row.get("started_at") or ""
        risk = row.get("risk_level") or "low"
        is_current = sid == current_id
        btn_label = f"{'• ' if is_current else ''}{label}"

        open_col, menu_col = st.columns([4, 1])
        with open_col:
            if st.button(
                btn_label,
                key=f"hist_{sid}",
                use_container_width=True,
                disabled=is_current,
                help=f"{started} · {risk}",
            ):
                if load_past_session(sid):
                    st.rerun()
                else:
                    st.caption("No messages in that session yet.")

        with menu_col:
            with st.popover(ui.get("manage", "⋯"), use_container_width=True):
                st.caption(label)
                new_title = st.text_input(
                    ui.get("rename", "Rename"),
                    value=label if (row.get("title") or "").strip() else "",
                    key=f"rename_input_{sid}",
                    placeholder=ui.get("rename_placeholder", "Conversation title"),
                    label_visibility="collapsed",
                )
                if st.button(
                    ui.get("rename_save", "Save"),
                    key=f"rename_save_{sid}",
                    use_container_width=True,
                ):
                    if uid and rename_session(sid, int(uid), new_title or label):
                        if on_mutate:
                            on_mutate()
                        st.rerun()
                    else:
                        st.caption("Could not rename.")

                md = None
                if uid:
                    md = export_session_markdown(sid, int(uid))
                if md:
                    safe_name = "".join(
                        c if c.isalnum() or c in ("-", "_") else "_"
                        for c in (label[:40] or f"session_{sid}")
                    )
                    st.download_button(
                        ui.get("export_md", "Export (.md)"),
                        data=md.encode("utf-8"),
                        file_name=f"sakoon_{safe_name}.md",
                        mime="text/markdown",
                        key=f"export_md_{sid}",
                        use_container_width=True,
                    )

                confirm = st.checkbox(
                    ui.get("delete_confirm", "Confirm delete"),
                    key=f"del_confirm_{sid}",
                )
                if st.button(
                    ui.get("delete", "Delete"),
                    key=f"del_btn_{sid}",
                    use_container_width=True,
                    type="secondary",
                    disabled=not confirm,
                ):
                    if uid and delete_session(sid, int(uid)):
                        if is_current:
                            start_new_chat()
                        if on_mutate:
                            on_mutate()
                        st.rerun()
                    else:
                        st.caption("Could not delete.")
