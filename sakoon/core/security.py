"""Security helpers — HTML escaping for Streamlit/email surfaces."""

from __future__ import annotations

import html


def escape_html(value: object) -> str:
    """Escape dynamic text before unsafe_allow_html interpolation."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


# Public crisis resources (trusted constants — not user input)
HELPLINE_NUMBER = "0311-7786264"
HELPLINE_NAME = "Umang Mental Health Helpline (Pakistan)"
