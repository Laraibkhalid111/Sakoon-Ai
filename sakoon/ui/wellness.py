"""Wellness room UI — mood log, journal, affirmations, resources, exercises."""

from __future__ import annotations

import streamlit as st

from sakoon.core.security import escape_html
from sakoon.db import add_journal_entry, add_mood_log, get_journal_entries, get_mood_logs
from sakoon.services.wellness import (
    affirmation_for_today,
    emergency_resources,
    list_affirmations,
    mood_label,
    wellness_ui_copy,
)
from sakoon.ui.coping import COPING_ACTIONS, start_coping


def render_wellness_nav(lang: str) -> str:
    """Sidebar Chat / Wellness / Insights switcher. Returns selected view key."""
    from sakoon.services.insights import insights_ui_copy

    copy = wellness_ui_copy(lang)
    icopy = insights_ui_copy(lang)
    current = st.session_state.get("main_view", "chat")
    cols = st.columns(3)
    with cols[0]:
        if st.button(
            copy["nav_chat"],
            key="nav_chat",
            use_container_width=True,
            type="primary" if current == "chat" else "secondary",
        ):
            st.session_state.main_view = "chat"
            st.rerun()
    with cols[1]:
        if st.button(
            copy["nav_wellness"],
            key="nav_wellness",
            use_container_width=True,
            type="primary" if current == "wellness" else "secondary",
        ):
            st.session_state.main_view = "wellness"
            st.rerun()
    with cols[2]:
        if st.button(
            icopy["nav"],
            key="nav_insights",
            use_container_width=True,
            type="primary" if current == "insights" else "secondary",
        ):
            st.session_state.main_view = "insights"
            st.rerun()
    return st.session_state.get("main_view", "chat")


def render_wellness_page(lang: str) -> None:
    """Full wellness room (mood, journal, affirmations, resources, exercises)."""
    copy = wellness_ui_copy(lang)
    sid = st.session_state.get("db_session_id")
    uid = st.session_state.get("db_user_id")

    st.markdown(f"## {copy['title']}")
    st.caption(copy["subtitle"])

    tab_mood, tab_journal, tab_affirm, tab_resources, tab_ex = st.tabs(
        [
            copy["tab_mood"],
            copy["tab_journal"],
            copy["tab_affirm"],
            copy["tab_resources"],
            copy["tab_exercises"],
        ]
    )

    with tab_mood:
        _render_mood_tab(copy, lang, sid, uid)

    with tab_journal:
        _render_journal_tab(copy, sid, uid)

    with tab_affirm:
        _render_affirm_tab(copy, lang)

    with tab_resources:
        _render_resources_tab(copy, lang)

    with tab_ex:
        st.caption(copy["exercises_hint"])
        labels = {
            "breathing_exercise": "Breathing" if lang != "urdu" else "سانس",
            "grounding_exercise": "Grounding" if lang != "urdu" else "گراؤنڈنگ",
            "journaling_prompt": "Journal" if lang != "urdu" else "جرنل",
        }
        cols = st.columns(3)
        for i, action in enumerate(COPING_ACTIONS):
            with cols[i]:
                if st.button(labels[action], key=f"well_ex_{action}", use_container_width=True):
                    start_coping(action)
                    st.session_state.main_view = "chat"
                    st.rerun()


def _render_mood_tab(copy: dict, lang: str, sid, uid) -> None:
    rating = st.slider(copy["mood_prompt"], min_value=1, max_value=10, value=5, key="well_mood_slider")
    st.caption(mood_label(rating, lang))
    note = st.text_input(copy["mood_note"], key="well_mood_note")
    if st.button(copy["mood_save"], type="primary", key="well_mood_save"):
        new_id = add_mood_log(
            rating=rating,
            note=note,
            session_id=sid,
            user_id=uid,
            source="manual",
        )
        if new_id:
            st.session_state.mood = rating
            profile = st.session_state.setdefault("profile", {})
            profile["mood_rating"] = rating
            st.session_state.profile = profile
            st.success(copy["mood_saved"])
        else:
            st.session_state.db_error = True
            st.warning("Could not save mood — you can keep going.")

    st.markdown(f"#### {copy['mood_history']}")
    logs = get_mood_logs(limit=12, user_id=uid)
    if not logs:
        st.caption(copy["empty"])
    else:
        for row in logs:
            label = mood_label(int(row["rating"]), lang)
            note_bit = f" — {row['note']}" if row.get("note") else ""
            st.markdown(
                f"- **{int(row['rating'])}/10** ({escape_html(label)})"
                f"{escape_html(note_bit)} · `{escape_html(str(row.get('created_at') or ''))}`"
            )


def _render_journal_tab(copy: dict, sid, uid) -> None:
    st.markdown(f"**{copy['journal_prompt']}**")
    body = st.text_area(
        "journal_body",
        height=160,
        placeholder=copy["journal_placeholder"],
        label_visibility="collapsed",
        key="well_journal_body",
    )
    if st.button(copy["journal_save"], type="primary", key="well_journal_save"):
        new_id = add_journal_entry(
            body=body,
            prompt=copy["journal_prompt"],
            session_id=sid,
            user_id=uid,
        )
        if new_id:
            notes = st.session_state.setdefault("journal_notes", [])
            notes.append(body.strip())
            if "well_journal_body" in st.session_state:
                del st.session_state["well_journal_body"]
            st.success(copy["journal_saved"])
            st.rerun()
        else:
            if not (body or "").strip():
                st.warning(copy["empty"])
            else:
                st.session_state.db_error = True
                st.warning("Could not save journal — you can keep going.")

    st.markdown(f"#### {copy['journal_history']}")
    entries = get_journal_entries(limit=10, user_id=uid)
    if not entries:
        st.caption(copy["empty"])
    else:
        for row in entries:
            st.markdown(f"**{escape_html(str(row.get('created_at') or ''))}**")
            if row.get("prompt"):
                st.caption(row["prompt"])
            st.write(row.get("body") or "")
            st.divider()


def _render_affirm_tab(copy: dict, lang: str) -> None:
    today = affirmation_for_today(lang)
    st.markdown(
        f'<div class="sakoon-coping-card"><h3>{escape_html(copy["affirm_today"])}</h3>'
        f'<div class="sakoon-coping-step">{escape_html(today)}</div></div>',
        unsafe_allow_html=True,
    )
    with st.expander(copy["affirm_more"], expanded=False):
        for line in list_affirmations(lang):
            st.markdown(f"- {line}")


def _render_resources_tab(copy: dict, lang: str) -> None:
    st.markdown(f"#### {copy['resources_title']}")
    st.info(copy["resources_note"])
    for res in emergency_resources(lang):
        st.markdown(
            f"**{escape_html(res['name'])}**  \n"
            f"{escape_html(res['detail'])}  \n"
            f"*{escape_html(copy['when'])}* {escape_html(res['when'])}"
        )
        st.divider()
