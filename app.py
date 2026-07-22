"""
app.py — Sakoon AI
Thin Streamlit entrypoint: page config + orchestration only.
UI and business logic live under sakoon/.
"""

import streamlit as st

from sakoon.core.config import get_settings
from sakoon.core.logging import setup_logging
from sakoon.ui.chat_loop import render_chat_view
from sakoon.ui.components import crisis_copy, inject_styles
from sakoon.ui.insights import render_insights_page
from sakoon.ui.sidebar import render_sidebar
from sakoon.ui.state import bootstrap_local_db, init_session_state, resolve_language_override
from sakoon.ui.wellness import render_wellness_page

setup_logging(get_settings().log_level)

st.set_page_config(
    page_title="Sakoon AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
inject_styles(
    st.session_state.get("theme", "light"),
    view=st.session_state.get("main_view", "chat"),
)
bootstrap_local_db()
resolve_language_override()
render_sidebar()

# Alternate rooms
view = st.session_state.get("main_view", "chat")
if view in ("wellness", "insights"):
    if st.session_state.crisis_triggered:
        crisis_text, _ = crisis_copy(st.session_state.lang)
        st.markdown(
            f'<div class="sakoon-banner crisis">{crisis_text}</div>',
            unsafe_allow_html=True,
        )
    if view == "wellness":
        render_wellness_page(st.session_state.lang)
    else:
        render_insights_page(st.session_state.lang)
    st.stop()

render_chat_view()
