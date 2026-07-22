"""Local-mode sidebar helpers (no login / signup)."""

from __future__ import annotations

import streamlit as st


def render_local_sidebar_note() -> None:
    """Privacy note for local-only mode — no accounts."""
    st.caption("Local session · data stays on this device")
