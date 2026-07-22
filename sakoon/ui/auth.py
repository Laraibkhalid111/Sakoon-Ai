"""Local-mode sidebar helpers (no login / signup)."""

from __future__ import annotations

import streamlit as st

from sakoon.ui.shell import chrome_copy


def render_local_sidebar_note(lang: str | None = None) -> None:
    """Privacy note for local-only mode — no accounts."""
    resolved = lang or st.session_state.get("lang", "english")
    st.caption(chrome_copy(resolved)["local_note"])
