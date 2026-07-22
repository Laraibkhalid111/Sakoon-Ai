"""Phase 2 UI helpers — markdown safety + coping copy."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sakoon.ui.coping import COPING_ACTIONS, get_coping_copy  # noqa: E402
from sakoon.ui.markdown import markdown_to_safe_html  # noqa: E402


def test_markdown_escapes_script_tags():
    html_out = markdown_to_safe_html('Hello <script>alert(1)</script> **world**')
    assert "<script>" not in html_out
    assert "<strong>world</strong>" in html_out
    assert "&lt;script&gt;" in html_out


def test_markdown_lists_and_code():
    src = "Try this:\n\n- breathe\n- notice\n\nUse `calm` now."
    html_out = markdown_to_safe_html(src)
    assert "<ul>" in html_out
    assert "<li>breathe</li>" in html_out
    assert "<code>calm</code>" in html_out


def test_markdown_fenced_code():
    src = "Example:\n\n```python\nprint('<hi>')\n```"
    html_out = markdown_to_safe_html(src)
    assert "<pre" in html_out
    assert "&lt;hi&gt;" in html_out
    assert "<hi>" not in html_out


def test_markdown_simple_table():
    src = "| Mood | Tip |\n| --- | --- |\n| Low | Breathe |\n| High | Walk |"
    html_out = markdown_to_safe_html(src)
    assert "<table" in html_out
    assert "<th>Mood</th>" in html_out
    assert "<td>Breathe</td>" in html_out


def test_copy_helper_no_onclick_in_bubble_module():
    import inspect
    from sakoon.ui import components as c

    src = inspect.getsource(c)
    assert "onclick=" not in src
    assert "clipboard_write" in src


def test_coping_copy_all_actions():
    for action in COPING_ACTIONS:
        en = get_coping_copy(action, "english")
        ur = get_coping_copy(action, "urdu")
        assert en.get("title")
        assert ur.get("title")
        if action != "journaling_prompt":
            assert len(en.get("steps", [])) >= 3
