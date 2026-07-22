"""Main chat view — messages, generation, crisis gate, input queue."""

from __future__ import annotations

from datetime import timedelta

import streamlit as st

from sakoon.core.metrics import emit
from sakoon.core.rate_limit import allow_chat
from sakoon.core.validation import validate_email, validate_name, validate_phone
from sakoon.db import (
    add_mood_log,
    delete_last_assistant_message,
    ensure_session_title_from_text,
    log_message,
    update_session,
    update_user,
    upsert_snapshot,
)
from sakoon.services.chatbot import stream_ai_response
from sakoon.services.prompts import ERROR_COPY
from sakoon.services.reply_policy import (
    apply_language_from_response,
    avatar_initials,
    choose_assistant_reply,
    merge_extracted_fields,
    rate_limit_message,
)
from sakoon.services.safety import check_crisis
from sakoon.ui.components import (
    banner,
    crisis_copy,
    redirect_copy,
    render_bubble,
    render_scroll_to_bottom,
    render_stop_bar,
    render_thinking_bar,
    render_voice_composer,
    timestamp_now,
)
from sakoon.ui.coping import render_coping_panel, start_coping
from sakoon.ui.session_ops import cancel_ai_turn
from sakoon.ui.shell import render_chat_shell_intro
from sakoon.ui.sidebar import invalidate_session_caches


def render_chat_view() -> None:
    """Render chat chrome, history, voice, input, and drive pending generation."""
    if st.session_state.crisis_triggered:
        crisis_text, _ = crisis_copy(st.session_state.lang)
        st.markdown(
            f'<div class="sakoon-banner crisis">{crisis_text}</div>',
            unsafe_allow_html=True,
        )

    render_coping_panel(st.session_state.lang)
    render_chat_shell_intro(st.session_state.lang, len(st.session_state.messages))

    if st.session_state.thinking:
        if render_stop_bar(st.session_state.lang):
            cancel_ai_turn()
            st.session_state._gen_grace_done = False
            emit("chat_stop", user_id=st.session_state.get("db_user_id"))
            st.rerun()

    if st.session_state.show_error == "groq":
        lang = st.session_state.lang
        banner("error", f"❌ {ERROR_COPY['groq_failure']['ur' if lang == 'urdu' else 'en']}")

    if st.session_state.db_error:
        lang = st.session_state.lang
        banner("warning", f"⚠️ {ERROR_COPY['db_failure']['ur' if lang == 'urdu' else 'en']}")
        st.session_state.db_error = False

    _render_message_list()
    render_scroll_to_bottom(auto=bool(st.session_state.pop("auto_scroll", False)))
    render_voice_composer(st.session_state.lang, disabled=bool(st.session_state.thinking))

    user_input = st.chat_input(
        _chat_placeholder(),
        disabled=st.session_state.thinking,
    )

    if st.session_state.pop("regenerate_requested", False) and not st.session_state.thinking:
        if queue_regenerate():
            st.session_state._gen_grace_done = False
            st.rerun()

    drive_pending_generation()
    handle_incoming_user_turn(user_input)


def _chat_placeholder() -> str:
    if st.session_state.thinking:
        return "...ساکون سوچ رہا ہے" if st.session_state.lang == "urdu" else "Sakoon is thinking..."
    if st.session_state.lang == "urdu":
        return "آپ کیسا محسوس کر رہے ہیں، لکھیں..."
    return "Type how you're feeling..."


def _render_message_list() -> None:
    user_avatar = avatar_initials((st.session_state.profile.get("name") or "You"))
    last_idx = len(st.session_state.messages) - 1
    for idx, msg in enumerate(st.session_state.messages):
        is_last_assistant = (
            idx == last_idx
            and msg["role"] == "assistant"
            and not msg.get("is_redirect", False)
            and not st.session_state.thinking
            and not st.session_state.get("session_closed")
        )
        render_bubble(
            role=msg["role"],
            text=msg["content"],
            is_redirect=msg.get("is_redirect", False),
            is_voice=msg.get("is_voice", False),
            ts=msg.get("ts"),
            msg_index=idx,
            enable_markdown=(msg["role"] == "assistant" and not msg.get("is_redirect", False)),
            show_regenerate=is_last_assistant,
            avatar_label="S" if msg["role"] == "assistant" else user_avatar,
        )


def queue_regenerate() -> bool:
    """Drop last assistant reply (memory + DB) and re-queue the preceding user turn."""
    msgs = st.session_state.messages
    if len(msgs) < 2 or msgs[-1].get("role") != "assistant":
        return False
    msgs.pop()
    hist = st.session_state.groq_history
    if hist and hist[-1].get("role") == "assistant":
        hist.pop()
    sid = st.session_state.get("db_session_id")
    if sid:
        if not delete_last_assistant_message(int(sid)):
            st.session_state.db_error = True
    last_user = next((m for m in reversed(msgs) if m.get("role") == "user"), None)
    if not last_user:
        return False
    st.session_state.pending_ai_turn = {
        "raw": last_user.get("content") or "",
        "is_voice": bool(last_user.get("is_voice")),
        "regenerate": True,
    }
    st.session_state.thinking = True
    st.session_state.cancel_generation = False
    st.session_state._gen_grace_done = False
    emit("chat_regenerate", user_id=st.session_state.get("db_user_id"))
    return True


def drive_pending_generation() -> None:
    """Fragment-driven start with a short grace window so Stop can cancel pending work."""
    if not (st.session_state.pending_ai_turn and st.session_state.thinking):
        return

    @st.fragment(run_every=timedelta(milliseconds=450))
    def _drive() -> None:
        if not st.session_state.get("thinking"):
            return
        if st.session_state.get("cancel_generation"):
            cancel_ai_turn()
            st.session_state._gen_grace_done = False
            st.rerun()
            return
        turn = st.session_state.get("pending_ai_turn")
        if not turn:
            return
        if not st.session_state.get("_gen_grace_done"):
            st.session_state._gen_grace_done = True
            return
        st.session_state.pending_ai_turn = None
        try:
            process_ai_turn(turn["raw"], turn.get("is_voice", False))
        finally:
            st.session_state.thinking = False
            st.session_state._gen_grace_done = False
            st.session_state.cancel_generation = False
            invalidate_session_caches()
        st.rerun()

    _drive()


def process_ai_turn(raw: str, is_voice: bool) -> None:
    """Stream Groq reply into the UI, then persist the final assistant turn."""
    stream_box = st.empty()
    response = None
    live_text = ""
    cancelled = False

    with stream_box.container():
        render_thinking_bar(st.session_state.lang)

    for event in stream_ai_response(
        st.session_state.groq_history,
        current_lang=st.session_state.lang,
    ):
        if st.session_state.get("cancel_generation"):
            cancelled = True
            break
        if event.get("type") == "delta":
            live_text = event.get("text") or ""
            with stream_box.container():
                render_bubble(
                    role="assistant",
                    text=live_text + (" ▍" if live_text != "…" else ""),
                    msg_index=99999,
                    enable_markdown=True,
                    show_actions=False,
                    avatar_label="S",
                )
        elif event.get("type") == "done":
            response = event.get("response")

    if cancelled:
        st.session_state.cancel_generation = False
        stream_box.empty()
        if live_text and live_text not in ("", "…"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": live_text,
                "is_redirect": False,
                "is_voice": False,
                "ts": timestamp_now(),
            })
            st.session_state.groq_history.append({
                "role": "assistant",
                "content": live_text,
            })
            sid = st.session_state.db_session_id
            if sid:
                log_message(sid, "assistant", live_text, input_mode="text")
        st.session_state.auto_scroll = True
        return

    if not isinstance(response, dict):
        from sakoon.services.chatbot import _default_response

        response = _default_response(st.session_state.lang)
        if live_text and live_text != "…":
            response["reply_to_user"] = live_text

    st.session_state.show_error = "groq" if response.get("_error") else None

    detected = response.get("detected_language", "english")
    st.session_state.detected_lang = detected
    st.session_state.lang = apply_language_from_response(
        detected,
        st.session_state.get("lang_override_select", "Auto"),
    )
    lang = st.session_state.lang
    st.session_state.stage = response.get("conversation_stage", st.session_state.stage)

    prev_mood = st.session_state.get("mood")
    profile, valid_name, valid_email, valid_phone, new_mood = merge_extracted_fields(
        st.session_state.profile,
        response.get("extracted", {}),
        validate_name=validate_name,
        validate_email=validate_email,
        validate_phone=validate_phone,
    )
    if new_mood is not None:
        st.session_state.mood = new_mood
        if prev_mood != new_mood:
            add_mood_log(
                rating=new_mood,
                note=None,
                session_id=st.session_state.get("db_session_id"),
                user_id=st.session_state.get("db_user_id"),
                source="chat",
            )

    suggested = response.get("suggested_coping_action")
    if suggested and suggested != "none":
        profile["suggested_coping_action"] = suggested
        coping = profile.get("coping_suggestions", [])
        if suggested not in coping:
            profile["coping_suggestions"] = coping + [suggested]
        start_coping(suggested)

    st.session_state.profile = profile

    reply_text, is_redirect = choose_assistant_reply(
        response,
        lang,
        valid_name=valid_name,
        valid_email=valid_email,
        valid_phone=valid_phone,
        redirect_copy=redirect_copy(lang),
    )

    with stream_box.container():
        render_bubble(
            role="assistant",
            text=reply_text,
            is_redirect=is_redirect,
            msg_index=99999,
            enable_markdown=not is_redirect,
            show_actions=False,
            avatar_label="S",
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply_text,
        "is_redirect": is_redirect,
        "is_voice": False,
        "ts": timestamp_now(),
    })
    st.session_state.groq_history.append({
        "role": "assistant",
        "content": reply_text,
    })

    sid = st.session_state.db_session_id
    if sid:
        if not log_message(sid, "assistant", reply_text, input_mode="text"):
            st.session_state.db_error = True

        if not upsert_snapshot(
            session_id=sid,
            mood_rating=profile.get("mood_rating"),
            symptoms=profile.get("symptoms", []),
            triggers=profile.get("possible_triggers", []),
            coping_suggestions=profile.get("coping_suggestions", []),
        ):
            st.session_state.db_error = True

        if profile.get("primary_concern"):
            update_session(sid, primary_concern=profile["primary_concern"])

        if profile.get("name") or profile.get("email"):
            uid = st.session_state.db_user_id
            if uid is not None:
                update_user(
                    uid,
                    name=profile.get("name"),
                    email=profile.get("email"),
                    phone=profile.get("phone"),
                    preferred_language=st.session_state.lang,
                )

    st.session_state.auto_scroll = True


def handle_incoming_user_turn(user_input: str | None) -> None:
    """Queue a user turn from chat input or confirmed voice transcript."""
    is_voice = False
    if st.session_state.pending_voice_text:
        raw = st.session_state.pending_voice_text
        st.session_state.pending_voice_text = None
        st.session_state.whisper_error = False
        is_voice = True
    elif user_input and user_input.strip() and not st.session_state.thinking:
        raw = user_input.strip()
    else:
        return

    st.session_state.messages.append({
        "role": "user",
        "content": raw,
        "is_redirect": False,
        "is_voice": is_voice,
        "ts": timestamp_now(),
    })
    st.session_state.groq_history.append({"role": "user", "content": raw})

    if check_crisis(raw):
        _handle_crisis_turn(raw, is_voice)
        return

    user_key = str(st.session_state.get("db_user_id") or "local")
    rl = allow_chat(user_key)
    if not rl.allowed:
        emit(
            "rate_limited_chat",
            user_id=st.session_state.get("db_user_id"),
            retry=round(rl.retry_after_sec, 1),
        )
        wait_s = max(1, int(rl.retry_after_sec) + 1)
        if st.session_state.groq_history and st.session_state.groq_history[-1].get("role") == "user":
            st.session_state.groq_history.pop()
        st.session_state.messages.append({
            "role": "assistant",
            "content": rate_limit_message(st.session_state.lang, wait_s),
            "is_redirect": True,
            "is_voice": False,
            "ts": timestamp_now(),
        })
        st.rerun()
        return

    emit("chat_turn_queued", user_id=st.session_state.get("db_user_id"), voice=is_voice)
    sid = st.session_state.db_session_id
    if sid:
        if not log_message(sid, "user", raw, input_mode="voice" if is_voice else "text"):
            st.session_state.db_error = True
        else:
            ensure_session_title_from_text(int(sid), raw)
            invalidate_session_caches()

    st.session_state.pending_ai_turn = {"raw": raw, "is_voice": is_voice}
    st.session_state.thinking = True
    st.session_state.cancel_generation = False
    st.session_state._gen_grace_done = False
    st.rerun()


def _handle_crisis_turn(raw: str, is_voice: bool) -> None:
    emit("crisis_detected", user_id=st.session_state.get("db_user_id"))
    st.session_state.crisis_triggered = True
    profile = st.session_state.profile
    risk_flags = profile.get("risk_flags", [])
    if "crisis_detected" not in risk_flags:
        profile["risk_flags"] = risk_flags + ["crisis_detected"]
    st.session_state.profile = profile

    _, crisis_reply = crisis_copy(st.session_state.lang)
    st.session_state.messages.append({
        "role": "assistant",
        "content": crisis_reply,
        "is_redirect": False,
        "is_voice": False,
        "ts": timestamp_now(),
    })
    st.session_state.groq_history.append({"role": "assistant", "content": crisis_reply})

    sid = st.session_state.db_session_id
    if sid:
        ok1 = log_message(sid, "user", raw, input_mode="voice" if is_voice else "text")
        ok2 = log_message(sid, "assistant", crisis_reply, input_mode="text")
        ok3 = update_session(sid, risk_level="crisis")
        if ok1:
            ensure_session_title_from_text(int(sid), raw)
            invalidate_session_caches()
        if not ok1 or not ok2 or not ok3:
            st.session_state.db_error = True
    st.rerun()
