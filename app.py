"""
app.py — Sakoon AI
Streamlit entrypoint: page config, CSS, sidebar, chat loop, session state.
"""

import re
import time
import streamlit as st

from prompts import WELCOME_MESSAGE, OFF_TOPIC_REDIRECT, ERROR_COPY
from chatbot import get_ai_response
from safety import check_crisis          # deterministic crisis detector — runs before every Groq call

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sakoon AI — Mental Wellness Companion",
    page_icon="🫶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS (DESIGN.md §4.2 + §15) ─────────────────────────────────────────────
CUSTOM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
<style>
:root {
  --color-primary: #5B8AA6;
  --color-primary-dark: #3F6C86;
  --color-primary-light: #EAF2F6;
  --color-secondary: #8FBFA6;
  --color-secondary-dark: #6E9C84;
  --color-accent: #D9A25C;
  --color-bg: #FAF9F7;
  --color-surface: #FFFFFF;
  --color-border: #E4E1DB;
  --color-text-primary: #2B2B2B;
  --color-text-secondary: #6B6B6B;
  --color-text-inverse: #FFFFFF;
  --color-success: #4C9A6A;
  --color-success-bg: #E9F5EC;
  --color-warning: #C98A2E;
  --color-warning-bg: #FBF1E1;
  --color-error: #C1553D;
  --color-error-bg: #FBEAE6;
  --color-crisis: #B23A48;
  --color-crisis-bg: #FBE9EA;
}

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, Segoe UI, sans-serif;
  background-color: var(--color-bg);
  color: var(--color-text-primary);
}

/* Sidebar */
[data-testid="stSidebar"] {
  background-color: var(--color-surface) !important;
  border-right: 1px solid var(--color-border);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }

/* Chat input */
[data-testid="stChatInput"] textarea {
  border: 1px solid var(--color-border) !important;
  border-radius: 12px !important;
  font-family: 'Inter', sans-serif;
  background: var(--color-surface) !important;
}
[data-testid="stChatInput"] textarea:focus {
  border: 2px solid var(--color-primary) !important;
  box-shadow: 0 0 0 3px rgba(91,138,166,0.15) !important;
}

/* Buttons */
.stButton > button {
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"],
.stButton > button:not([kind]) {
  background-color: var(--color-primary) !important;
  color: white !important;
  border: none !important;
}
.stButton > button:hover {
  background-color: var(--color-primary-dark) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(63,108,134,0.25) !important;
}

/* Chat bubbles */
.sakoon-bubble-wrap {
  display: flex;
  align-items: flex-end;
  margin-bottom: 14px;
  animation: fadeUp 0.2s ease;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}
.sakoon-bubble-wrap.user { justify-content: flex-end; }
.sakoon-bubble-wrap.assistant { justify-content: flex-start; }

.sakoon-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  margin-right: 8px;
}

.sakoon-bubble {
  max-width: 72%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.6;
  position: relative;
}
.sakoon-bubble.assistant {
  background: var(--color-primary-light);
  color: var(--color-text-primary);
  border-bottom-left-radius: 4px;
}
.sakoon-bubble.user {
  background: #F1F7F3;
  color: var(--color-text-primary);
  border-bottom-right-radius: 4px;
}
.sakoon-bubble.redirect {
  background: var(--color-warning-bg);
  border: 1px solid var(--color-warning);
  color: var(--color-text-primary);
  font-style: italic;
  border-radius: 10px;
  text-align: center;
  max-width: 80%;
  margin: 0 auto;
}
.sakoon-bubble.urdu {
  font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', serif;
  font-size: 17px;
  line-height: 1.8;
  direction: rtl;
  text-align: right;
}
.sakoon-ts {
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-top: 4px;
  text-align: right;
}

/* Typing indicator */
.sakoon-typing { display: flex; gap: 5px; padding: 4px 0; }
.sakoon-typing span {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--color-primary);
  animation: blink 1.2s infinite;
}
.sakoon-typing span:nth-child(2) { animation-delay: 0.2s; }
.sakoon-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink {
  0%,100% { opacity: 0.3; }
  50%      { opacity: 1; }
}

/* Banners */
.sakoon-banner {
  padding: 14px 18px;
  border-radius: 10px;
  margin-bottom: 12px;
  font-size: 14px;
  line-height: 1.5;
}
.sakoon-banner.error   { background: var(--color-error-bg);   border: 1px solid var(--color-error);   }
.sakoon-banner.warning { background: var(--color-warning-bg); border: 1px solid var(--color-warning); }
.sakoon-banner.success { background: var(--color-success-bg); border: 1px solid var(--color-success); }
.sakoon-banner.crisis  {
  background: var(--color-crisis-bg);
  border: 2px solid var(--color-crisis);
  font-size: 15px;
}

/* Language badge */
.sakoon-lang-badge {
  display: inline-block;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  font-family: 'Inter', sans-serif;
}

/* Mood pill */
.sakoon-mood-pill {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-family: 'Inter', sans-serif;
  color: white;
}

/* Disclaimer */
.sakoon-disclaimer {
  font-size: 11px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  text-align: center;
  padding: 12px 8px 0;
}

/* Hide Streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _is_urdu_script(text: str) -> bool:
    """Return True if text contains Arabic-range Unicode (Urdu script)."""
    return bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))


def _lang_key(lang: str) -> str:
    return lang if lang in ("english", "urdu", "roman_urdu", "mixed") else "english"


def _redirect_copy(lang: str) -> str:
    return OFF_TOPIC_REDIRECT.get(lang, OFF_TOPIC_REDIRECT["english"])


def _ts() -> str:
    return time.strftime("%I:%M %p")


def _render_bubble(role: str, text: str, is_redirect: bool = False, is_voice: bool = False):
    is_urdu = _is_urdu_script(text)
    urdu_cls = " urdu" if is_urdu else ""
    ts = _ts()

    if is_redirect:
        st.markdown(
            f'<div class="sakoon-bubble-wrap"><div class="sakoon-bubble redirect{urdu_cls}">'
            f'⚠️ {text}</div></div>',
            unsafe_allow_html=True,
        )
        return

    if role == "assistant":
        st.markdown(
            f'<div class="sakoon-bubble-wrap assistant">'
            f'<div class="sakoon-avatar">🫶</div>'
            f'<div>'
            f'<div class="sakoon-bubble assistant{urdu_cls}">{text}</div>'
            f'<div class="sakoon-ts">{ts}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    else:
        prefix = "🎙️ " if is_voice else ""
        st.markdown(
            f'<div class="sakoon-bubble-wrap user">'
            f'<div>'
            f'<div class="sakoon-bubble user{urdu_cls}">{prefix}{text}</div>'
            f'<div class="sakoon-ts" style="text-align:right">{ts}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def _render_typing():
    return st.markdown(
        '<div class="sakoon-bubble-wrap assistant">'
        '<div class="sakoon-avatar">🫶</div>'
        '<div class="sakoon-bubble assistant">'
        '<div class="sakoon-typing"><span></span><span></span><span></span></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )


def _mood_pill(rating: int | None) -> str:
    if rating is None:
        return ""
    if rating <= 3:
        color, label = "#D9A25C", "Having a hard time"
    elif rating <= 6:
        color, label = "#5B8AA6", "Getting through it"
    else:
        color, label = "#8FBFA6", "Feeling steady"
    return (
        f'<span class="sakoon-mood-pill" style="background:{color}">'
        f'🫧 Mood today: {label}</span>'
    )


def _lang_badge(lang: str) -> str:
    labels = {"english": "English", "urdu": "اردو", "roman_urdu": "Roman Urdu", "mixed": "Mixed"}
    return (
        f'<span class="sakoon-lang-badge">🌐 {labels.get(lang, "English")}</span>'
    )


def _banner(kind: str, text: str):
    st.markdown(
        f'<div class="sakoon-banner {kind}">{text}</div>',
        unsafe_allow_html=True,
    )


# ── Session state init ───────────────────────────────────────────────────────

def _init_state():
    defaults = {
        "messages": [],          # [{"role","content","is_redirect","is_voice"}]
        "groq_history": [],      # [{"role","content"}] — for Groq API
        "profile": {**WELCOME_MESSAGE["extracted"]},
        "stage": "greeting",
        "lang": "english",
        "mood": None,
        "crisis_triggered": False,
        "show_error": None,       # None | "groq" | "whisper"
        "thinking": False,
        "report_bytes": None,
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
        })
        st.session_state.groq_history.append({
            "role": "assistant",
            "content": w["reply_to_user"],
        })


_init_state()

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    # Branding (DESIGN.md §6.1)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">'
        '<span style="font-size:28px">🫶</span>'
        '<span style="font-family:Inter,sans-serif;font-size:18px;font-weight:600;'
        'color:#2B2B2B">Sakoon AI</span></div>',
        unsafe_allow_html=True,
    )
    tagline_ur = "بات کرنے کی ایک پرسکون جگہ" if st.session_state.lang == "urdu" else ""
    tagline_en = "A calm space to talk"
    st.markdown(
        f'<p style="font-size:12px;color:#6B6B6B;margin-top:0;margin-bottom:16px">'
        f'{tagline_en}'
        f'{"  ·  " + tagline_ur if tagline_ur else ""}</p>',
        unsafe_allow_html=True,
    )

    # Language badge + manual override
    st.markdown(_lang_badge(st.session_state.lang), unsafe_allow_html=True)
    lang_override = st.selectbox(
        "Language override",
        ["Auto", "English", "اردو"],
        label_visibility="collapsed",
        key="lang_override_select",
    )
    st.markdown('<hr style="border-color:#E4E1DB;margin:16px 0">', unsafe_allow_html=True)

    # Voice input (M4 — placeholder with note)
    with st.expander("🎙️ Voice Input", expanded=False):
        st.info("Voice input will be enabled in the next update (M4).", icon="🎙️")

    st.markdown('<hr style="border-color:#E4E1DB;margin:16px 0">', unsafe_allow_html=True)

    # Mood pill
    if st.session_state.mood is not None:
        st.markdown(_mood_pill(st.session_state.mood), unsafe_allow_html=True)
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # Report button (M5 — placeholder)
    if st.button("📄 Generate Report", use_container_width=True, key="btn_report"):
        st.info("Report generation will be available after the conversation develops (M5).")

    # Resend email button (M6 — placeholder)
    if st.button("📧 Resend to Email", use_container_width=True, key="btn_email"):
        st.info("Email delivery will be enabled in M6.")

    # Crisis helpline — always visible once triggered
    if st.session_state.crisis_triggered:
        st.markdown(
            '<div class="sakoon-banner crisis" style="margin-top:16px">'
            '💙 <strong>Need help now?</strong><br>'
            '📞 Umang Helpline: <strong>0311-7786264</strong></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr style="border-color:#E4E1DB;margin:16px 0">', unsafe_allow_html=True)
    st.markdown(
        '<p class="sakoon-disclaimer">🫶 Sakoon AI is not a substitute for '
        'professional mental health care. If you are in crisis, please contact '
        'a licensed professional or call <strong>0311-7786264</strong>.</p>',
        unsafe_allow_html=True,
    )


# ── Main chat area ────────────────────────────────────────────────────────────

# Crisis pinned card (DESIGN.md §7)
if st.session_state.crisis_triggered:
    lang = st.session_state.lang
    if lang == "urdu":
        crisis_text = (
            "💙 <strong>لگتا ہے آپ اس وقت کسی بہت مشکل دور سے گزر رہے ہیں۔ "
            "آپ کو یہ اکیلے نہیں سہنا۔</strong><br><br>"
            "📞 امنگ مینٹل ہیلتھ ہیلپ لائن (پاکستان): <strong>0311-7786264</strong><br>"
            "📞 یا اپنے قریبی ایمرجنسی نمبر پر<br><br>"
            "میں یہاں آپ سے بات کرنے کے لیے موجود ہوں، لیکن براہ کرم کسی ایسے "
            "شخص سے بھی رابطہ کریں جو آپ کے قریب ہو۔"
        )
    else:
        crisis_text = (
            "💙 <strong>It sounds like you're going through something really heavy right now. "
            "You don't have to face this alone.</strong><br><br>"
            "📞 Umang Mental Health Helpline (Pakistan): <strong>0311-7786264</strong><br>"
            "📞 Or your local emergency number<br><br>"
            "I'm still here to talk with you, but please also consider reaching "
            "a person who can be there with you."
        )
    st.markdown(
        f'<div class="sakoon-banner crisis">{crisis_text}</div>',
        unsafe_allow_html=True,
    )

# Error banner (DESIGN.md §8)
if st.session_state.show_error == "groq":
    lang = st.session_state.lang
    msg = ERROR_COPY["groq_failure"]["ur" if lang == "urdu" else "en"]
    _banner("error", f"❌ {msg}")

# Chat history
for msg in st.session_state.messages:
    _render_bubble(
        role=msg["role"],
        text=msg["content"],
        is_redirect=msg.get("is_redirect", False),
        is_voice=msg.get("is_voice", False),
    )

# Typing indicator placeholder
thinking_placeholder = st.empty()

# ── Chat input handling ───────────────────────────────────────────────────────

placeholder_text = (
    "آپ کیسا محسوس کر رہے ہیں، لکھیں..."
    if st.session_state.lang == "urdu"
    else "Type how you're feeling..."
)

user_input = st.chat_input(placeholder_text, disabled=st.session_state.thinking)

if user_input and user_input.strip():
    raw = user_input.strip()

    # ── SAFETY CHECK — runs deterministically BEFORE Groq (IDEA.md §8) ────
    # This is a hard check — it cannot be prompted away. If it fires, the
    # normal LLM reply is bypassed entirely for this turn.
    is_crisis = check_crisis(raw)

    # ── Add user message to display + Groq history ─────────────────────────
    st.session_state.messages.append({
        "role": "user",
        "content": raw,
        "is_redirect": False,
        "is_voice": False,
    })
    st.session_state.groq_history.append({"role": "user", "content": raw})

    if is_crisis:
        # ── CRISIS BRANCH — bypass Groq, set flags, rerun ─────────────────
        # The pinned crisis card (rendered at top of main area on rerun)
        # IS the response for this turn. The chat continues normally below it.
        if not st.session_state.crisis_triggered:
            st.session_state.crisis_triggered = True
        profile = st.session_state.profile
        risk_flags = profile.get("risk_flags", [])
        if "crisis_detected" not in risk_flags:
            profile["risk_flags"] = risk_flags + ["crisis_detected"]
        st.session_state.profile = profile
        # No Groq call — no assistant bubble added for this turn.
        # The crisis card pinned at the top is the visible response.
        st.rerun()

    else:
        # ── NORMAL BRANCH — call Groq ──────────────────────────────────────
        st.session_state.thinking = True
        with thinking_placeholder:
            _render_typing()

        response = get_ai_response(
            st.session_state.groq_history,
            current_lang=st.session_state.lang,
        )

        st.session_state.thinking = False
        thinking_placeholder.empty()

        # ── Handle error ──────────────────────────────────────────────────
        if response.get("_error"):
            st.session_state.show_error = "groq"
        else:
            st.session_state.show_error = None

        # ── Update session language ───────────────────────────────────────
        lang = response.get("detected_language", "english")
        if lang_override == "اردو":
            lang = "urdu"
        elif lang_override == "English":
            lang = "english"
        st.session_state.lang = lang

        # ── Update conversation stage ─────────────────────────────────────
        st.session_state.stage = response.get("conversation_stage", st.session_state.stage)

        # ── Merge extracted profile fields ────────────────────────────────
        ext = response.get("extracted", {})
        profile = st.session_state.profile
        for field in ("name", "email", "phone", "primary_concern"):
            if ext.get(field):
                profile[field] = ext[field]
        if ext.get("mood_rating") is not None:
            profile["mood_rating"] = ext["mood_rating"]
            st.session_state.mood = ext["mood_rating"]
        for list_field in ("symptoms", "possible_triggers", "risk_flags"):
            existing = profile.get(list_field, [])
            new_items = ext.get(list_field, [])
            merged = list(dict.fromkeys(existing + new_items))
            profile[list_field] = merged
        st.session_state.profile = profile

        # ── Determine reply (off-topic override per DESIGN.md §8) ─────────
        is_on_topic = response.get("is_on_topic", True)
        if not is_on_topic:
            reply_text = _redirect_copy(lang)
            is_redirect = True
        else:
            reply_text = response.get("reply_to_user", "...")
            is_redirect = False

        # ── Add assistant message ─────────────────────────────────────────
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply_text,
            "is_redirect": is_redirect,
            "is_voice": False,
        })
        st.session_state.groq_history.append({
            "role": "assistant",
            "content": reply_text,
        })

        st.rerun()
