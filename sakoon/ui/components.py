"""Chat chrome helpers — bubbles, banners, badges, crisis copy, theme."""

from __future__ import annotations

import base64
import re
import time

import streamlit as st
import streamlit.components.v1 as components

from sakoon.core.security import HELPLINE_NAME, HELPLINE_NUMBER, escape_html
from sakoon.services.prompts import OFF_TOPIC_REDIRECT
from sakoon.ui.markdown import markdown_to_safe_html


def is_urdu_script(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", text or ""))


def lang_key(lang: str) -> str:
    return lang if lang in ("english", "urdu", "roman_urdu", "mixed") else "english"


def redirect_copy(lang: str) -> str:
    return OFF_TOPIC_REDIRECT.get(lang, OFF_TOPIC_REDIRECT["english"])


def timestamp_now() -> str:
    return time.strftime("%I:%M %p")


def crisis_copy(lang: str) -> tuple[str, str]:
    """Return (pinned_card_html, assistant_reply). Card HTML is trusted static markup."""
    if lang == "urdu":
        card = (
            "💙 <strong>لگتا ہے آپ اس وقت کسی بہت مشکل دور سے گزر رہے ہیں۔ "
            "آپ کو یہ اکیلے نہیں سہنا۔ اگر آپ فوری خطرے میں ہیں یا خود کو نقصان پہنچانے کا "
            "سوچ رہے ہیں، تو ابھی رابطہ کریں:</strong><br><br>"
            f"📞 امنگ مینٹل ہیلتھ ہیلپ لائن (پاکستان): <strong>{HELPLINE_NUMBER}</strong><br>"
            "📞 یا اپنے قریبی ایمرجنسی نمبر پر<br><br>"
            "میں یہاں آپ سے بات کرنے کے لیے موجود ہوں، لیکن براہ کرم کسی ایسے "
            "شخص سے بھی رابطہ کریں جو آپ کے قریب ہو۔"
        )
        reply = (
            "میں آپ کی بات سن رہا ہوں، اور ایسا لگتا ہے کہ آپ بہت زیادہ تکلیف میں ہیں۔ "
            "میں نے اس چیٹ کے اوپر مدد کے لیے معلومات فراہم کی ہیں تاکہ وہ آسانی سے مل سکیں۔ "
            "براہ کرم ابھی ان سے یا کسی قریبی شخص سے رابطہ کریں۔ میں اب بھی آپ سے بات کرنے کے لیے یہاں موجود ہوں۔"
        )
    elif lang == "roman_urdu":
        card = (
            "💙 <strong>Lagta hai aap bohot mushkil waqt se guzar rahe hain. "
            "Aap ko yeh akelay nahi sehna. Agar aap khatre mein hain ya khud ko nuksan "
            "pahunchane ka soch rahe hain, to abhi rabta karein:</strong><br><br>"
            f"📞 {escape_html(HELPLINE_NAME)}: <strong>{HELPLINE_NUMBER}</strong><br>"
            "📞 Ya apna local emergency number<br><br>"
            "Main yahan baat karne ke liye maujood hoon, lekin kisi qareebi shakhs "
            "se bhi rabta zaroor karein."
        )
        reply = (
            "Main aapki baat sun raha/rahi hoon, aur lagta hai aap bohot dard mein hain. "
            "Maine chat ke upar helpline ki maloomat rakh di hain. "
            "Please unse ya kisi trusted person se abhi rabta karein. Main ab bhi yahan hoon."
        )
    else:
        card = (
            "💙 <strong>It sounds like you're going through something really heavy right now. "
            "You don't have to face this alone. If you're in immediate danger or thinking "
            "about harming yourself, please reach out right now:</strong><br><br>"
            f"📞 {escape_html(HELPLINE_NAME)}: <strong>{HELPLINE_NUMBER}</strong><br>"
            "📞 Or your local emergency number<br><br>"
            "I'm still here to talk with you, but please also consider reaching "
            "a person who can be there with you."
        )
        reply = (
            "I hear you, and it sounds like you're carrying a lot of pain. "
            "I have placed helpline resources at the top of our chat so they are easy to find. "
            "Please connect with them, or a trusted person, right now. I am still here to talk with you."
        )
    return card, reply


def clipboard_write(text: str) -> None:
    """Legacy auto-copy helper (unreliable after Streamlit rerun — prefer render_copy_button)."""
    payload = base64.b64encode((text or "").encode("utf-8")).decode("ascii")
    components.html(
        f"""
        <script>
        (function() {{
          try {{
            const raw = atob("{payload}");
            const bytes = Uint8Array.from(raw, function(c) {{ return c.charCodeAt(0); }});
            const text = new TextDecoder("utf-8").decode(bytes);
            navigator.clipboard.writeText(text);
          }} catch (e) {{}}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def render_copy_button(text: str, key: str) -> None:
    """
    Copy control that keeps the user gesture: real <button> inside components.html.
    (st.button + post-rerun clipboard write usually fails silently.)
    """
    payload = base64.b64encode((text or "").encode("utf-8")).decode("ascii")
    safe_key = escape_html(key)
    components.html(
        f"""
        <button id="sakoon-copy-{safe_key}" type="button"
          style="font-family:Outfit,system-ui,sans-serif;font-size:12px;font-weight:600;
                 color:#0F766E;background:#CCFBF1;border:1px solid #99F6E4;
                 border-radius:10px;padding:4px 10px;cursor:pointer;">
          Copy
        </button>
        <script>
        (function() {{
          const btn = document.getElementById("sakoon-copy-{safe_key}");
          if (!btn) return;
          btn.addEventListener("click", async function() {{
            try {{
              const raw = atob("{payload}");
              const bytes = Uint8Array.from(raw, function(c) {{ return c.charCodeAt(0); }});
              const text = new TextDecoder("utf-8").decode(bytes);
              await navigator.clipboard.writeText(text);
              btn.textContent = "Copied";
              setTimeout(function() {{ btn.textContent = "Copy"; }}, 1200);
            }} catch (e) {{
              btn.textContent = "Failed";
              setTimeout(function() {{ btn.textContent = "Copy"; }}, 1200);
            }}
          }});
        }})();
        </script>
        """,
        height=36,
    )


def render_bubble(
    role: str,
    text: str,
    is_redirect: bool = False,
    is_voice: bool = False,
    ts: str | None = None,
    msg_index: int = 0,
    enable_markdown: bool = True,
    show_actions: bool = True,
    show_regenerate: bool = False,
    avatar_label: str | None = None,
) -> None:
    """Render a chat bubble. Copy uses st.button + clipboard JS (never onclick in markdown)."""
    urdu_cls = " urdu" if is_urdu_script(text) else ""
    stamp = escape_html(ts or timestamp_now())
    mark = escape_html((avatar_label or ("S" if role == "assistant" else "U"))[:2])

    if is_redirect:
        safe = escape_html(text or "")
        st.markdown(
            f'<div class="sakoon-bubble-wrap"><div class="sakoon-bubble redirect{urdu_cls}">'
            f"⚠️ {safe}</div></div>",
            unsafe_allow_html=True,
        )
        return

    if role == "assistant" and enable_markdown:
        body = markdown_to_safe_html(text or "")
    else:
        body = escape_html(text or "").replace("\n", "<br>")

    if role == "assistant":
        st.markdown(
            f'<div class="sakoon-bubble-wrap assistant">'
            f'<div class="sakoon-avatar" aria-hidden="true">{mark}</div>'
            f'<div class="sakoon-bubble-col">'
            f'<div class="sakoon-bubble assistant{urdu_cls}">{body}</div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )
        if show_actions:
            _render_message_actions(
                text=text or "",
                stamp=stamp,
                key_prefix=f"a_{msg_index}",
                align_end=False,
                show_regenerate=show_regenerate,
            )
    else:
        prefix = '<span class="sakoon-voice-badge">Voice</span> ' if is_voice else ""
        st.markdown(
            f'<div class="sakoon-bubble-wrap user">'
            f'<div class="sakoon-bubble-col user">'
            f'<div class="sakoon-bubble user{urdu_cls}">{prefix}{body}</div>'
            f"</div>"
            f'<div class="sakoon-avatar user-avatar" aria-hidden="true">{mark}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
        if show_actions:
            _render_message_actions(
                text=text or "",
                stamp=stamp,
                key_prefix=f"u_{msg_index}",
                align_end=True,
                show_regenerate=False,
            )


def _render_message_actions(
    text: str,
    stamp: str,
    key_prefix: str,
    align_end: bool = False,
    show_regenerate: bool = False,
) -> None:
    """Timestamp + Copy (+ optional Regenerate)."""
    if align_end:
        cols = st.columns([1, 1, 4])
        with cols[0]:
            render_copy_button(text, key=f"u_{key_prefix}")
        with cols[2]:
            st.markdown(
                f'<div class="sakoon-meta-row" style="justify-content:flex-end">'
                f'<span class="sakoon-ts">{stamp}</span></div>',
                unsafe_allow_html=True,
            )
    else:
        cols = st.columns([4, 1, 1] if show_regenerate else [5, 1])
        with cols[0]:
            st.markdown(
                f'<div class="sakoon-meta-row"><span class="sakoon-ts">{stamp}</span></div>',
                unsafe_allow_html=True,
            )
        with cols[1]:
            render_copy_button(text, key=f"a_{key_prefix}")
        if show_regenerate:
            with cols[2]:
                if st.button("Regen", key=f"regen_{key_prefix}", help="Regenerate reply"):
                    st.session_state.regenerate_requested = True
                    st.rerun()


def render_scroll_to_bottom() -> None:
    """Lightweight jump-to-latest control for long chats."""
    if st.button("↓ Latest", key="scroll_latest", help="Jump to latest message"):
        components.html(
            """
            <script>
            (function() {
              const doc = window.parent.document;
              const main = doc.querySelector('[data-testid="stAppViewContainer"]');
              if (main) main.scrollTo({ top: main.scrollHeight, behavior: 'smooth' });
              const body = doc.scrollingElement || doc.documentElement;
              body.scrollTo({ top: body.scrollHeight, behavior: 'smooth' });
            })();
            </script>
            """,
            height=0,
            width=0,
        )


def render_thinking_bar(lang: str) -> None:
    label = "...ساکون جواب لکھ رہا ہے" if lang == "urdu" else "Sakoon is composing a reply…"
    st.markdown(
        f'<div class="sakoon-thinking-bar" role="status" aria-live="polite">'
        f'<div class="sakoon-typing"><span></span><span></span><span></span></div>'
        f"<span>{escape_html(label)}</span></div>",
        unsafe_allow_html=True,
    )


def mood_pill_html(rating: int | None, lang: str = "english") -> str:
    if rating is None:
        return ""
    if lang == "urdu":
        prefix = "🫧 آج کا مزاج: "
        if rating <= 3:
            bg, text, label = "var(--color-warning-bg)", "var(--color-warning)", "مشکل وقت"
        elif rating <= 6:
            bg, text, label = "var(--color-primary-light)", "var(--color-primary-dark)", "بس گزر رہا ہے"
        else:
            bg, text, label = "var(--color-success-bg)", "var(--color-secondary-dark)", "بہتر اور مستحکم ہے"
    else:
        prefix = "🫧 Mood today: "
        if rating <= 3:
            bg, text, label = "var(--color-warning-bg)", "var(--color-warning)", "Having a hard time"
        elif rating <= 6:
            bg, text, label = "var(--color-primary-light)", "var(--color-primary-dark)", "Getting through it"
        else:
            bg, text, label = "var(--color-success-bg)", "var(--color-secondary-dark)", "Feeling steady"

    return (
        f'<span class="sakoon-mood-pill" style="background:{bg}; color:{text}; font-weight: 600;">'
        f"{prefix}{label}</span>"
    )


def lang_badge_html(lang: str) -> str:
    labels = {"english": "English", "urdu": "اردو", "roman_urdu": "Roman Urdu", "mixed": "Mixed"}
    return f'<span class="sakoon-lang-badge">🌐 {labels.get(lang, "English")}</span>'


def banner(kind: str, text: str) -> None:
    st.markdown(
        f'<div class="sakoon-banner {escape_html(kind)}">{escape_html(text)}</div>',
        unsafe_allow_html=True,
    )


def inject_styles(theme: str = "light") -> None:
    from sakoon.ui.styles import CUSTOM_CSS

    st.markdown(re.sub(r"\n\s*\n", "\n", CUSTOM_CSS), unsafe_allow_html=True)
    is_dark = "true" if theme == "dark" else "false"
    components.html(
        f"""
        <script>
        (function() {{
          const doc = window.parent.document;
          const app = doc.querySelector('.stApp');
          if (!app) return;
          if ({is_dark}) {{
            app.classList.add('sakoon-theme-dark');
          }} else {{
            app.classList.remove('sakoon-theme-dark');
          }}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def render_brand_header(lang: str) -> None:
    tagline_ur = "بات کرنے کی ایک پرسکون جگہ" if lang == "urdu" else ""
    tagline_en = "A calm space to talk"
    extra = f"  ·  {tagline_ur}" if tagline_ur else ""
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">'
        '<span class="sakoon-brand-mark" aria-hidden="true">S</span>'
        '<span class="sakoon-brand-title">Sakoon AI</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="sakoon-brand-tag">{escape_html(tagline_en + extra)}</p>',
        unsafe_allow_html=True,
    )
