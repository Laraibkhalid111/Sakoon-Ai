"""
app.py — Sakoon AI
Streamlit entrypoint: page config, sidebar, chat loop, session state.
Business logic lives under sakoon/ (Phase 1 package layout).
"""

import streamlit as st

from sakoon.core.logging import setup_logging, get_logger
from sakoon.core.config import get_settings
from sakoon.core.security import HELPLINE_NUMBER, HELPLINE_NAME, escape_html
from sakoon.core.validation import validate_name, validate_email, validate_phone
from sakoon.core.rate_limit import allow_chat
from sakoon.core.metrics import emit
from sakoon.core.health import check_health
from sakoon.services.prompts import WELCOME_MESSAGE, ERROR_COPY
from sakoon.services.chatbot import stream_ai_response, transcribe_audio, generate_report_narrative
from sakoon.services.safety import check_crisis
from sakoon.db import (
    init_db, update_user, create_session, update_session,
    close_session, log_message, upsert_snapshot, get_recent_sessions,
    add_mood_log, delete_last_assistant_message, ensure_session_title_from_text,
)
from sakoon.services.report import build_report, build_session_data
from sakoon.services.emailer import send_email_report
from sakoon.ui.components import (
    inject_styles, crisis_copy, render_bubble, render_thinking_bar,
    mood_pill_html, lang_badge_html, banner, redirect_copy, timestamp_now,
    render_brand_header, render_scroll_to_bottom,
)
from sakoon.ui.coping import render_coping_panel, start_coping, COPING_ACTIONS
from sakoon.ui.session_ops import (
    start_new_chat, load_past_session, ensure_local_identity, render_conversation_history,
)
from sakoon.ui.wellness import render_wellness_nav, render_wellness_page
from sakoon.ui.insights import render_insights_page
from sakoon.ui.auth import render_local_sidebar_note
from sakoon.ui.shell import chrome_copy, render_chat_shell_intro


@st.cache_data(ttl=20, show_spinner=False)
def _cached_recent_sessions(user_id: int | None, limit: int = 8) -> list:
    """Short-lived cache — avoids hitting SQLite on every unrelated widget rerun."""
    return get_recent_sessions(limit=limit, user_id=user_id)


def _invalidate_session_caches() -> None:
    _cached_recent_sessions.clear()

setup_logging(get_settings().log_level)
log = get_logger(__name__)

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sakoon AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

def _init_state():
    defaults = {
        "messages": [],          # [{"role","content","is_redirect","is_voice"}]
        "groq_history": [],      # [{"role","content"}] — for Groq API
        "profile": {**WELCOME_MESSAGE["extracted"]},
        "stage": "greeting",
        "lang": "english",
        "detected_lang": "english",
        "mood": None,
        "crisis_triggered": False,
        "show_error": None,       # None | "groq" | "whisper"
        "db_error": False,        # True when a non-critical DB write fails
        "thinking": False,
        "report_bytes": None,
        "last_session_data": None,
        "last_narrative": None,
        # DB identifiers (populated after first message)
        "db_session_id": None,
        "db_user_id": None,
        # Voice pipeline state
        "whisper_error": False,   # True when Whisper call fails
        "pending_voice_text": None,  # Transcript ready to inject as a message
        "voice_recorder_key": 0,
        # Anti double-submit: queue user turn, process Groq on next run
        "pending_ai_turn": None,  # {"raw": str, "is_voice": bool} | None
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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Inject welcome message once
    if not st.session_state.messages:
        w = WELCOME_MESSAGE
        st.session_state.messages.append({
            "role": "assistant",
            "content": w["reply_to_user"],
            "is_redirect": False,
            "is_voice": False,
            "ts": timestamp_now(),
        })
        st.session_state.groq_history.append({
            "role": "assistant",
            "content": w["reply_to_user"],
        })


_init_state()
inject_styles(
    st.session_state.get("theme", "light"),
    view=st.session_state.get("main_view", "chat"),
)

# ── DB init + local identity (no login) ───────────────────────────────────────
_db_ok = init_db()
if _db_ok and not st.session_state.get("_health_logged"):
    health = check_health()
    emit("app_ready", ok=health.get("ok"), has_groq=health.get("settings", {}).get("has_groq"))
    st.session_state._health_logged = True

if _db_ok:
    ensure_local_identity(preferred_language=st.session_state.get("lang", "english"))

# Session for local user
if _db_ok and st.session_state.db_session_id is None:
    sid = create_session(user_id=st.session_state.get("db_user_id"))
    if sid:
        st.session_state.db_session_id = sid

# Resolve language override immediately (T7.1)
lang_override = st.session_state.get("lang_override_select", "Auto")
if lang_override == "English":
    st.session_state.lang = "english"
elif lang_override == "اردو":
    st.session_state.lang = "urdu"
else:
    st.session_state.lang = st.session_state.get("detected_lang", "english")

# ── Sidebar ──────────────────────────────────────────────────────────────────

_ui = chrome_copy(st.session_state.lang)

with st.sidebar:
    render_brand_header(st.session_state.lang)
    render_local_sidebar_note(st.session_state.lang)

    # Theme + new chat
    theme_cols = st.columns(2)
    with theme_cols[0]:
        dark_on = st.toggle(
            _ui["dark"],
            value=st.session_state.theme == "dark",
            key="theme_toggle",
            help="Toggle calm dark theme",
        )
        new_theme = "dark" if dark_on else "light"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()
    with theme_cols[1]:
        if st.button(_ui["new_chat"], use_container_width=True, key="btn_new_chat"):
            start_new_chat()
            _invalidate_session_caches()
            st.rerun()

    render_wellness_nav(st.session_state.lang)

    # Language badge + manual override
    st.markdown(lang_badge_html(st.session_state.lang), unsafe_allow_html=True)
    lang_override = st.selectbox(
        "Language override",
        ["Auto", "English", "اردو"],
        label_visibility="collapsed",
        key="lang_override_select",
    )

    if st.session_state.mood is not None:
        st.markdown(mood_pill_html(st.session_state.mood, st.session_state.lang), unsafe_allow_html=True)

    with st.expander(_ui["voice"], expanded=False):
        st.caption(_ui["voice_hint"])
        lang = st.session_state.lang
        if st.session_state.thinking:
            st.caption(_ui["voice_paused"])
            audio_val = None
        else:
            audio_val = st.audio_input(
                label="Record your message",
                key=f"voice_recorder_{st.session_state.voice_recorder_key}",
                label_visibility="collapsed",
            )

        if audio_val is not None:
            audio_bytes = audio_val.read()
            with st.spinner("Transcribing…" if lang != "urdu" else "لکھا جا رہا ہے…"):
                transcript = transcribe_audio(audio_bytes, filename="voice.wav")

            if transcript:
                st.session_state.pending_voice_text = transcript
                st.session_state.whisper_error = False
                st.session_state.voice_recorder_key += 1
                st.rerun()
            else:
                st.session_state.whisper_error = True
                st.session_state.voice_recorder_key += 1
                st.rerun()

        if st.session_state.whisper_error:
            fail_copy = (
                ERROR_COPY["whisper_failure"]["ur"]
                if lang == "urdu"
                else ERROR_COPY["whisper_failure"]["en"]
            )
            banner("warning", f"⚠️ {fail_copy}")

    # Calming exercises (manual entry)
    with st.expander(
        _ui["calming"],
        expanded=bool(st.session_state.active_coping),
    ):
        labels = {
            "breathing_exercise": "Breathing" if st.session_state.lang != "urdu" else "سانس",
            "grounding_exercise": "Grounding" if st.session_state.lang != "urdu" else "گراؤنڈنگ",
            "journaling_prompt": "Journal" if st.session_state.lang != "urdu" else "جرنل",
        }
        ccols = st.columns(3)
        for i, action in enumerate(COPING_ACTIONS):
            with ccols[i]:
                if st.button(labels[action], key=f"btn_start_{action}", use_container_width=True):
                    start_coping(action)
                    st.rerun()

    # Persistent emergency support (DESIGN.md §7.4)
    with st.expander(
        _ui["help_now"],
        expanded=bool(st.session_state.crisis_triggered),
    ):
        if st.session_state.lang == "urdu":
            st.markdown(
                f"**امنگ مینٹل ہیلتھ ہیلپ لائن:** `{HELPLINE_NUMBER}`  \n"
                "اگر آپ خطرے میں ہیں تو قریبی ایمرجنسی نمبر پر بھی کال کریں۔"
            )
        elif st.session_state.lang == "roman_urdu":
            st.markdown(
                f"**{HELPLINE_NAME}:** `{HELPLINE_NUMBER}`  \n"
                "Agar aap khatre mein hain to local emergency number par bhi call karein."
            )
        else:
            st.markdown(
                f"**{HELPLINE_NAME}:** `{HELPLINE_NUMBER}`  \n"
                "If you are in immediate danger, also call your local emergency number."
            )

    # Past sessions — open / rename / export / delete
    recent = _cached_recent_sessions(st.session_state.get("db_user_id"), limit=12)
    with st.expander(_ui["history"], expanded=False):
        render_conversation_history(
            recent,
            _ui,
            on_mutate=_invalidate_session_caches,
        )

    # Report / email — collapsed to keep sidebar light
    with st.expander(_ui["report"], expanded=bool(st.session_state.report_bytes)):
        can_report = len(st.session_state.messages) >= 2
        if st.button(
            _ui["generate_report"],
            use_container_width=True,
            key="btn_report",
            disabled=not can_report,
            type="primary",
        ):
            lang = st.session_state.lang
            with st.spinner("Building your report..." if lang != "urdu" else "رپورٹ تیار کی جا رہی ہے..."):
                session_data = build_session_data(st.session_state)
                narrative = generate_report_narrative(session_data)
                pdf_bytes = build_report(session_data, narrative=narrative)

            if pdf_bytes:
                st.session_state.report_bytes = pdf_bytes
                st.session_state.last_session_data = session_data
                st.session_state.last_narrative = narrative
                _invalidate_session_caches()

                sid = st.session_state.db_session_id
                if sid and not st.session_state.session_closed:
                    if close_session(sid):
                        st.session_state.session_closed = True

                email = session_data.get("email")
                if email and email.strip():
                    with st.spinner("Sending wellness report email..." if lang != "urdu" else "ای میل بھیجی جا رہی ہے..."):
                        sent_ok = send_email_report(
                            recipient=email.strip(),
                            pdf_bytes=pdf_bytes,
                            filename="Sakoon_Wellness_Report.pdf",
                            session_data=session_data,
                            narrative=narrative
                        )
                    if sent_ok:
                        success_email_msg = (
                            "رپورٹ تیار ہے اور آپ کی ای میل پر بھیج دی گئی ہے!"
                            if lang == "urdu" else
                            "Your report is ready and has been emailed to you!"
                        )
                        st.success(f"✅ {success_email_msg}")
                    else:
                        warning_email_msg = ERROR_COPY["smtp_failure"]["ur" if lang == "urdu" else "en"]
                        st.warning(f"⚠️ {warning_email_msg}")
                else:
                    success_msg = (
                        "رپورٹ تیار ہے! نیچے سے ڈاؤن لوڈ کریں۔"
                        if lang == "urdu" else
                        "Your report is ready! Download it below."
                    )
                    st.success(f"✅ {success_msg}")
            else:
                err_copy = ERROR_COPY["pdf_failure"]["ur" if lang == "urdu" else "en"]
                st.error(f"❌ {err_copy}")

        if st.session_state.report_bytes:
            st.download_button(
                label=_ui["download_pdf"],
                data=st.session_state.report_bytes,
                file_name="Sakoon_Wellness_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="btn_download",
            )

        if st.button(_ui["resend_email"], use_container_width=True, key="btn_email", type="secondary"):
            lang = st.session_state.lang
            email = st.session_state.profile.get("email")

            if not email or not email.strip():
                no_email_msg = (
                    "ای میل ایڈریس موجود نہیں ہے۔ براہ کرم پہلے گفتگو میں اپنی ای میل شیئر کریں۔"
                    if lang == "urdu" else
                    "No email address is on file. Please share your email address in the chat first."
                )
                st.warning(f"⚠️ {no_email_msg}")
            elif not st.session_state.report_bytes:
                no_report_msg = (
                    "پہلے رپورٹ تیار کرنے کے لیے 'رپورٹ بنائیں' پر کلک کریں۔"
                    if lang == "urdu" else
                    "Please generate a report first by clicking 'Generate Report'."
                )
                st.warning(f"⚠️ {no_report_msg}")
            else:
                with st.spinner("Resending report email..." if lang != "urdu" else "ای میل دوبارہ بھیجی جا رہی ہے..."):
                    sent_ok = send_email_report(
                        recipient=email.strip(),
                        pdf_bytes=st.session_state.report_bytes,
                        filename="Sakoon_Wellness_Report.pdf",
                        session_data=st.session_state.get("last_session_data", build_session_data(st.session_state)),
                        narrative=st.session_state.get("last_narrative", "")
                    )
                if sent_ok:
                    success_email_msg = (
                        "آپ کی رپورٹ ای میل کر دی گئی ہے۔"
                        if lang == "urdu" else
                        "Your report has been emailed to you."
                    )
                    st.success(f"✅ {success_email_msg}")
                else:
                    warning_email_msg = ERROR_COPY["smtp_failure"]["ur" if lang == "urdu" else "en"]
                    st.warning(f"⚠️ {warning_email_msg}")

    st.markdown(
        f'<p class="sakoon-disclaimer">{escape_html(_ui["disclaimer"])} '
        f'<strong>{HELPLINE_NUMBER}</strong>.</p>',
        unsafe_allow_html=True,
    )


# ── Main content ──────────────────────────────────────────────────────────────

if st.session_state.get("main_view") == "wellness":
    # Crisis resources stay reachable from wellness Help tab; still pin if active
    if st.session_state.crisis_triggered:
        crisis_text, _ = crisis_copy(st.session_state.lang)
        st.markdown(
            f'<div class="sakoon-banner crisis">{crisis_text}</div>',
            unsafe_allow_html=True,
        )
    render_wellness_page(st.session_state.lang)
    st.stop()

if st.session_state.get("main_view") == "insights":
    if st.session_state.crisis_triggered:
        crisis_text, _ = crisis_copy(st.session_state.lang)
        st.markdown(
            f'<div class="sakoon-banner crisis">{crisis_text}</div>',
            unsafe_allow_html=True,
        )
    render_insights_page(st.session_state.lang)
    st.stop()

# ── Main chat area ────────────────────────────────────────────────────────────

# Crisis pinned card (DESIGN.md §7) — exact hard-coded copy, never LLM-generated
if st.session_state.crisis_triggered:
    crisis_text, _ = crisis_copy(st.session_state.lang)
    st.markdown(
        f'<div class="sakoon-banner crisis">{crisis_text}</div>',
        unsafe_allow_html=True,
    )

# Interactive coping / breathing / journal panel
render_coping_panel(st.session_state.lang)

render_chat_shell_intro(st.session_state.lang, len(st.session_state.messages))

# Error banner (DESIGN.md §8)
if st.session_state.show_error == "groq":
    lang = st.session_state.lang
    msg = ERROR_COPY["groq_failure"]["ur" if lang == "urdu" else "en"]
    banner("error", f"❌ {msg}")

# Non-alarming DB write failure banner (DESIGN.md §8)
if st.session_state.db_error:
    lang = st.session_state.lang
    msg = ERROR_COPY["db_failure"]["ur" if lang == "urdu" else "en"]
    banner("warning", f"⚠️ {msg}")
    st.session_state.db_error = False

def _avatar_initials() -> str:
    name = (st.session_state.profile.get("name") or "You").strip()
    parts = name.replace("_", " ").split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return (name[:2] if len(name) > 1 else name[:1] or "Y").upper()

_user_avatar = _avatar_initials()
_last_idx = len(st.session_state.messages) - 1

# Chat history
for idx, msg in enumerate(st.session_state.messages):
    is_last_assistant = (
        idx == _last_idx
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
        avatar_label="S" if msg["role"] == "assistant" else _user_avatar,
    )

render_scroll_to_bottom()

# ── Chat input handling ───────────────────────────────────────────────────────

# Placeholder swaps to 'Sakoon is thinking...' while disabled — DESIGN.md §6.4
if st.session_state.thinking:
    placeholder_text = (
        "...ساکون سوچ رہا ہے" if st.session_state.lang == "urdu" else "Sakoon is thinking..."
    )
else:
    placeholder_text = (
        "آپ کیسا محسوس کر رہے ہیں، لکھیں..."
        if st.session_state.lang == "urdu"
        else "Type how you're feeling..."
    )

user_input = st.chat_input(placeholder_text, disabled=st.session_state.thinking)


def _queue_regenerate() -> bool:
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
    emit("chat_regenerate", user_id=st.session_state.get("db_user_id"))
    return True


def _process_ai_turn(raw: str, is_voice: bool) -> None:
    """Stream Groq reply into the UI, then persist the final assistant turn."""
    stream_box = st.empty()
    response = None
    live_text = ""

    with stream_box.container():
        render_thinking_bar(st.session_state.lang)

    for event in stream_ai_response(
        st.session_state.groq_history,
        current_lang=st.session_state.lang,
    ):
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

    if not isinstance(response, dict):
        from sakoon.services.chatbot import _default_response
        response = _default_response(st.session_state.lang)
        if live_text and live_text != "…":
            response["reply_to_user"] = live_text

    # ── Handle error ──────────────────────────────────────────────────
    if response.get("_error"):
        st.session_state.show_error = "groq"
    else:
        st.session_state.show_error = None

    # ── Update session language ───────────────────────────────────────
    detected = response.get("detected_language", "english")
    st.session_state.detected_lang = detected

    lang_override_val = st.session_state.get("lang_override_select", "Auto")
    if lang_override_val == "English":
        st.session_state.lang = "english"
    elif lang_override_val == "اردو":
        st.session_state.lang = "urdu"
    else:
        st.session_state.lang = detected

    lang = st.session_state.lang
    st.session_state.stage = response.get("conversation_stage", st.session_state.stage)

    # ── Merge extracted profile fields & validate (DESIGN.md §8, T7.4) ──
    ext = response.get("extracted", {})
    profile = st.session_state.profile

    valid_name, name_val = validate_name(ext.get("name"))
    if valid_name and name_val:
        profile["name"] = name_val
    elif ext.get("name"):
        valid_name = False
    else:
        valid_name = True

    valid_email, email_val = validate_email(ext.get("email"))
    if valid_email and email_val:
        profile["email"] = email_val
    elif ext.get("email"):
        valid_email = False
    else:
        valid_email = True

    valid_phone, phone_val = validate_phone(ext.get("phone"))
    if valid_phone and phone_val:
        profile["phone"] = phone_val
    elif ext.get("phone"):
        valid_phone = False
    else:
        valid_phone = True

    if ext.get("primary_concern"):
        profile["primary_concern"] = ext["primary_concern"]

    if ext.get("mood_rating") is not None:
        new_mood = ext["mood_rating"]
        prev_mood = st.session_state.get("mood")
        profile["mood_rating"] = new_mood
        st.session_state.mood = new_mood
        # Persist only when mood changes (avoid duplicate rows each turn)
        if prev_mood != new_mood:
            add_mood_log(
                rating=new_mood,
                note=None,
                session_id=st.session_state.get("db_session_id"),
                user_id=st.session_state.get("db_user_id"),
                source="chat",
            )

    for list_field in ("symptoms", "possible_triggers", "risk_flags"):
        existing = profile.get(list_field, [])
        new_items = ext.get(list_field, [])
        merged = list(dict.fromkeys(existing + new_items))
        profile[list_field] = merged

    # Track coping suggestion and open interactive panel
    suggested = response.get("suggested_coping_action")
    if suggested and suggested != "none":
        profile["suggested_coping_action"] = suggested
        coping = profile.get("coping_suggestions", [])
        if suggested not in coping:
            profile["coping_suggestions"] = coping + [suggested]
        start_coping(suggested)

    st.session_state.profile = profile

    # ── Determine reply (off-topic / validation override per DESIGN.md §8) ──
    is_on_topic = response.get("is_on_topic", True)
    is_redirect = False

    if not is_on_topic:
        reply_text = redirect_copy(lang)
        is_redirect = True
    elif not valid_name:
        reply_text = "مجھے آپ کا نام سمجھ نہیں آیا — میں آپ کو کیا کہہ کر بلاؤں؟" if lang == "urdu" else "I didn't quite catch your name — what should I call you?"
    elif not valid_email:
        reply_text = "یہ مکمل ای میل نہیں لگ رہی — ایک بار دوبارہ چیک کر لیں؟" if lang == "urdu" else "That doesn't look like a complete email — mind double-checking it?"
    elif not valid_phone:
        reply_text = "براہ کرم اپنا نمبر کوڈ کے ساتھ لکھیں، مثلاً +923001234567" if lang == "urdu" else "Could you share your number with the country code, like +923001234567?"
    else:
        reply_text = response.get("reply_to_user", "...")
        is_redirect = False

    # Show final text in the live slot (avoids empty flash before rerun)
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

    # ── Persist: log assistant msg, upsert snapshot, update user/session ─
    profile = st.session_state.profile
    sid = st.session_state.db_session_id
    if sid:
        if not log_message(sid, "assistant", reply_text, input_mode="text"):
            st.session_state.db_error = True

        ok = upsert_snapshot(
            session_id=sid,
            mood_rating=profile.get("mood_rating"),
            symptoms=profile.get("symptoms", []),
            triggers=profile.get("possible_triggers", []),
            coping_suggestions=profile.get("coping_suggestions", []),
        )
        if not ok:
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


# Process regenerate request (from last assistant "Regen" button)
if st.session_state.pop("regenerate_requested", False) and not st.session_state.thinking:
    if _queue_regenerate():
        st.rerun()

# Process queued AI turn from previous run (input stays disabled while thinking)
if st.session_state.pending_ai_turn and st.session_state.thinking:
    turn = st.session_state.pending_ai_turn
    st.session_state.pending_ai_turn = None
    try:
        _process_ai_turn(turn["raw"], turn.get("is_voice", False))
    finally:
        st.session_state.thinking = False
        _invalidate_session_caches()
    st.rerun()

# ── Determine raw input (voice transcript takes priority over typed) ──────────
_is_voice_turn = False
if st.session_state.pending_voice_text:
    raw_input = st.session_state.pending_voice_text
    st.session_state.pending_voice_text = None
    st.session_state.whisper_error = False
    _is_voice_turn = True
elif user_input and user_input.strip() and not st.session_state.thinking:
    raw_input = user_input.strip()
else:
    raw_input = None

if raw_input:
    raw = raw_input

    # ── SAFETY CHECK — runs deterministically BEFORE Groq (IDEA.md §8) ────
    is_crisis = check_crisis(raw)

    st.session_state.messages.append({
        "role": "user",
        "content": raw,
        "is_redirect": False,
        "is_voice": _is_voice_turn,
        "ts": timestamp_now(),
    })
    st.session_state.groq_history.append({"role": "user", "content": raw})

    if is_crisis:
        emit("crisis_detected", user_id=st.session_state.get("db_user_id"))
        if not st.session_state.crisis_triggered:
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
            ok1 = log_message(sid, "user", raw, input_mode="voice" if _is_voice_turn else "text")
            ok2 = log_message(sid, "assistant", crisis_reply, input_mode="text")
            ok3 = update_session(sid, risk_level="crisis")
            if ok1:
                ensure_session_title_from_text(int(sid), raw)
                _invalidate_session_caches()
            if not ok1 or not ok2 or not ok3:
                st.session_state.db_error = True

        st.rerun()

    else:
        # Rate-limit Groq path only (crisis replies always allowed)
        user_key = str(st.session_state.get("db_user_id") or "local")
        rl = allow_chat(user_key)
        if not rl.allowed:
            emit("rate_limited_chat", user_id=st.session_state.get("db_user_id"), retry=round(rl.retry_after_sec, 1))
            wait_s = max(1, int(rl.retry_after_sec) + 1)
            slow_msg = (
                f"You're sending messages a bit quickly. Please wait about {wait_s} seconds, then try again."
                if st.session_state.lang != "urdu"
                else f"آپ تھوڑے تیزی سے پیغام بھیج رہے ہیں۔ براہِ کرم تقریباً {wait_s} سیکنڈ انتظار کریں۔"
            )
            # Keep user text in the UI, but do not pollute Groq context or DB
            if st.session_state.groq_history and st.session_state.groq_history[-1].get("role") == "user":
                st.session_state.groq_history.pop()
            st.session_state.messages.append({
                "role": "assistant",
                "content": slow_msg,
                "is_redirect": True,
                "is_voice": False,
                "ts": timestamp_now(),
            })
            st.rerun()

        emit("chat_turn_queued", user_id=st.session_state.get("db_user_id"), voice=_is_voice_turn)
        # Queue Groq work for the next run so chat_input can disable while thinking
        sid = st.session_state.db_session_id
        if sid:
            if not log_message(sid, "user", raw, input_mode="voice" if _is_voice_turn else "text"):
                st.session_state.db_error = True
            else:
                ensure_session_title_from_text(int(sid), raw)
                _invalidate_session_caches()

        st.session_state.pending_ai_turn = {"raw": raw, "is_voice": _is_voice_turn}
        st.session_state.thinking = True
        st.rerun()
