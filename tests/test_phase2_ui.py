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


def test_partial_reply_extract_from_stream_buffer():
    from sakoon.services.chatbot import _extract_partial_reply, _extract_is_on_topic

    buf = '{"reply_to_user": "Hello there", "conversation_stage": "greeting"'
    assert _extract_partial_reply(buf) == "Hello there"
    partial = '{"reply_to_user": "Hi \\nfriend'
    assert "Hi" in _extract_partial_reply(partial)
    assert _extract_is_on_topic('{"is_on_topic": false, "reply_to_user": "x"') is False
    assert _extract_is_on_topic('{"is_on_topic": true') is True
    assert _extract_is_on_topic('{"reply_to_user": "x"') is None


def test_copy_uses_iframe_button_not_st_button_clipboard():
    import inspect
    from sakoon.ui import components as c

    src = inspect.getsource(c.render_copy_button)
    assert "navigator.clipboard.writeText" in src
    assert "addEventListener" in src


def test_coping_copy_all_actions():
    for action in COPING_ACTIONS:
        en = get_coping_copy(action, "english")
        ur = get_coping_copy(action, "urdu")
        assert en.get("title")
        assert ur.get("title")
        if action != "journaling_prompt":
            assert len(en.get("steps", [])) >= 3


def test_chrome_copy_bilingual_keys():
    from sakoon.ui.shell import chrome_copy, shell_view_class

    required = {
        "nav_label", "dark", "new_chat", "copy", "regen", "latest",
        "disclaimer", "chat_hint", "local_note", "voice", "report",
        "rename", "delete", "export_md", "manage",
    }
    for lang in ("english", "urdu", "roman_urdu"):
        ui = chrome_copy(lang)
        assert required.issubset(ui.keys())
        assert all(ui[k] for k in required)

    assert shell_view_class("chat") == "sakoon-view-chat"
    assert shell_view_class("wellness") == "sakoon-view-wellness"
    assert shell_view_class("insights") == "sakoon-view-insights"


def test_inject_styles_applies_view_class():
    import inspect
    from sakoon.ui import components as c

    src = inspect.getsource(c.inject_styles)
    assert "shell_view_class" in src
    assert "sakoon-view-chat" in src
