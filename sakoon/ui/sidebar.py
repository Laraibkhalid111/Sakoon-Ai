"""Sidebar chrome — theme, nav, coping, history, report/email."""

from __future__ import annotations

import streamlit as st

from sakoon.core.security import HELPLINE_NAME, HELPLINE_NUMBER, escape_html
from sakoon.db import close_session, get_recent_sessions
from sakoon.services.chatbot import generate_report_narrative
from sakoon.services.emailer import send_email_report
from sakoon.services.prompts import ERROR_COPY
from sakoon.services.report import build_report, build_session_data
from sakoon.ui.auth import render_local_sidebar_note
from sakoon.ui.components import (
    lang_badge_html,
    mood_pill_html,
    render_brand_header,
)
from sakoon.ui.coping import COPING_ACTIONS, start_coping
from sakoon.ui.session_ops import render_conversation_history, start_new_chat
from sakoon.ui.shell import chrome_copy
from sakoon.ui.wellness import render_wellness_nav


@st.cache_data(ttl=20, show_spinner=False)
def cached_recent_sessions(user_id: int | None, limit: int = 8) -> list:
    """Short-lived cache — avoids hitting SQLite on every unrelated widget rerun."""
    return get_recent_sessions(limit=limit, user_id=user_id)


def invalidate_session_caches() -> None:
    cached_recent_sessions.clear()


def render_sidebar() -> dict:
    """Render the full sidebar. Returns chrome copy for the active language."""
    ui = chrome_copy(st.session_state.lang)

    with st.sidebar:
        render_brand_header(st.session_state.lang)
        render_local_sidebar_note(st.session_state.lang)

        theme_cols = st.columns(2)
        with theme_cols[0]:
            dark_on = st.toggle(
                ui["dark"],
                value=st.session_state.theme == "dark",
                key="theme_toggle",
                help="Toggle calm dark theme",
            )
            new_theme = "dark" if dark_on else "light"
            if new_theme != st.session_state.theme:
                st.session_state.theme = new_theme
                st.rerun()
        with theme_cols[1]:
            if st.button(ui["new_chat"], use_container_width=True, key="btn_new_chat"):
                start_new_chat()
                invalidate_session_caches()
                st.rerun()

        render_wellness_nav(st.session_state.lang)

        st.markdown(lang_badge_html(st.session_state.lang), unsafe_allow_html=True)
        st.selectbox(
            "Language override",
            ["Auto", "English", "اردو"],
            label_visibility="collapsed",
            key="lang_override_select",
        )

        if st.session_state.mood is not None:
            st.markdown(
                mood_pill_html(st.session_state.mood, st.session_state.lang),
                unsafe_allow_html=True,
            )

        with st.expander(ui["voice"], expanded=False):
            st.caption(ui["voice_card_hint"])
            if st.session_state.thinking:
                st.caption(ui["voice_paused"])

        with st.expander(ui["calming"], expanded=bool(st.session_state.active_coping)):
            labels = {
                "breathing_exercise": "Breathing" if st.session_state.lang != "urdu" else "سانس",
                "grounding_exercise": "Grounding" if st.session_state.lang != "urdu" else "گراؤنڈنگ",
                "journaling_prompt": "Journal" if st.session_state.lang != "urdu" else "جرنل",
            }
            cols = st.columns(3)
            for i, action in enumerate(COPING_ACTIONS):
                with cols[i]:
                    if st.button(labels[action], key=f"btn_start_{action}", use_container_width=True):
                        start_coping(action)
                        st.rerun()

        with st.expander(ui["help_now"], expanded=bool(st.session_state.crisis_triggered)):
            _render_helpline(st.session_state.lang)

        recent = cached_recent_sessions(st.session_state.get("db_user_id"), limit=12)
        with st.expander(ui["history"], expanded=False):
            render_conversation_history(
                recent,
                ui,
                on_mutate=invalidate_session_caches,
            )

        with st.expander(ui["report"], expanded=bool(st.session_state.report_bytes)):
            _render_report_panel(ui)

        st.markdown(
            f'<p class="sakoon-disclaimer">{escape_html(ui["disclaimer"])} '
            f'<strong>{HELPLINE_NUMBER}</strong>.</p>',
            unsafe_allow_html=True,
        )

    return ui


def _render_helpline(lang: str) -> None:
    if lang == "urdu":
        st.markdown(
            f"**امنگ مینٹل ہیلتھ ہیلپ لائن:** `{HELPLINE_NUMBER}`  \n"
            "اگر آپ خطرے میں ہیں تو قریبی ایمرجنسی نمبر پر بھی کال کریں۔"
        )
    elif lang == "roman_urdu":
        st.markdown(
            f"**{HELPLINE_NAME}:** `{HELPLINE_NUMBER}`  \n"
            "Agar aap khatre mein hain to local emergency number par bhi call karein."
        )
    else:
        st.markdown(
            f"**{HELPLINE_NAME}:** `{HELPLINE_NUMBER}`  \n"
            "If you are in immediate danger, also call your local emergency number."
        )


def _render_report_panel(ui: dict) -> None:
    can_report = len(st.session_state.messages) >= 2
    if st.button(
        ui["generate_report"],
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
            invalidate_session_caches()

            sid = st.session_state.db_session_id
            if sid and not st.session_state.session_closed:
                if close_session(sid):
                    st.session_state.session_closed = True

            email = session_data.get("email")
            if email and email.strip():
                with st.spinner(
                    "Sending wellness report email..." if lang != "urdu" else "ای میل بھیجی جا رہی ہے..."
                ):
                    sent_ok = send_email_report(
                        recipient=email.strip(),
                        pdf_bytes=pdf_bytes,
                        filename="Sakoon_Wellness_Report.pdf",
                        session_data=session_data,
                        narrative=narrative,
                    )
                if sent_ok:
                    msg = (
                        "رپورٹ تیار ہے اور آپ کی ای میل پر بھیج دی گئی ہے!"
                        if lang == "urdu"
                        else "Your report is ready and has been emailed to you!"
                    )
                    st.success(f"✅ {msg}")
                else:
                    st.warning(
                        f"⚠️ {ERROR_COPY['smtp_failure']['ur' if lang == 'urdu' else 'en']}"
                    )
            else:
                msg = (
                    "رپورٹ تیار ہے! نیچے سے ڈاؤن لوڈ کریں۔"
                    if lang == "urdu"
                    else "Your report is ready! Download it below."
                )
                st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {ERROR_COPY['pdf_failure']['ur' if lang == 'urdu' else 'en']}")

    if st.session_state.report_bytes:
        st.download_button(
            label=ui["download_pdf"],
            data=st.session_state.report_bytes,
            file_name="Sakoon_Wellness_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="btn_download",
        )

    if st.button(ui["resend_email"], use_container_width=True, key="btn_email", type="secondary"):
        lang = st.session_state.lang
        email = st.session_state.profile.get("email")
        if not email or not email.strip():
            msg = (
                "ای میل ایڈریس موجود نہیں ہے۔ براہ کرم پہلے گفتگو میں اپنی ای میل شیئر کریں۔"
                if lang == "urdu"
                else "No email address is on file. Please share your email address in the chat first."
            )
            st.warning(f"⚠️ {msg}")
        elif not st.session_state.report_bytes:
            msg = (
                "پہلے رپورٹ تیار کرنے کے لیے 'رپورٹ بنائیں' پر کلک کریں۔"
                if lang == "urdu"
                else "Please generate a report first by clicking 'Generate Report'."
            )
            st.warning(f"⚠️ {msg}")
        else:
            with st.spinner(
                "Resending report email..." if lang != "urdu" else "ای میل دوبارہ بھیجی جا رہی ہے..."
            ):
                sent_ok = send_email_report(
                    recipient=email.strip(),
                    pdf_bytes=st.session_state.report_bytes,
                    filename="Sakoon_Wellness_Report.pdf",
                    session_data=st.session_state.get(
                        "last_session_data", build_session_data(st.session_state)
                    ),
                    narrative=st.session_state.get("last_narrative", ""),
                )
            if sent_ok:
                msg = (
                    "آپ کی رپورٹ ای میل کر دی گئی ہے۔"
                    if lang == "urdu"
                    else "Your report has been emailed to you."
                )
                st.success(f"✅ {msg}")
            else:
                st.warning(
                    f"⚠️ {ERROR_COPY['smtp_failure']['ur' if lang == 'urdu' else 'en']}"
                )
