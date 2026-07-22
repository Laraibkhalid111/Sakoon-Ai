"""Interactive coping exercises — breathing, grounding, journaling."""

from __future__ import annotations

from typing import Any

COPING_ACTIONS = ("breathing_exercise", "grounding_exercise", "journaling_prompt")

_COPY: dict[str, dict[str, Any]] = {
    "breathing_exercise": {
        "english": {
            "title": "Box breathing",
            "intro": "A simple 4-count breath to settle your nervous system. Follow each step at your own pace.",
            "steps": [
                "Sit comfortably. Soften your shoulders.",
                "Inhale slowly through your nose for 4 counts.",
                "Hold gently for 4 counts.",
                "Exhale slowly through your mouth for 4 counts.",
                "Hold empty for 4 counts. Repeat 3–4 rounds if it feels good.",
            ],
            "done": "Nice work. Notice how your body feels now — a little more space is enough.",
            "next": "Next step",
            "finish": "I'm done",
            "restart": "Start over",
        },
        "urdu": {
            "title": "باکس سانس",
            "intro": "چار گنتی کی سادہ سانس جو آپ کے اعصاب کو پرسکون کرنے میں مدد دے سکتی ہے۔",
            "steps": [
                "آرام سے بیٹھیں، کندھے نرم رکھیں۔",
                "ناک سے آہستہ چار گنتی تک سانس اندر لیں۔",
                "چار گنتی تک سانس روکے رکھیں۔",
                "منہ سے آہستہ چار گنتی تک سانس باہر نکالیں۔",
                "خالی رکھ کر چار گنتی رکیں۔ اگر اچھا لگے تو ۳–۴ دور دہرائیں۔",
            ],
            "done": "بہت اچھا۔ اب اپنے جسم پر توجہ دیں — تھوڑی سی سکون بھی کافی ہے۔",
            "next": "اگلا قدم",
            "finish": "میں نے مکمل کر لیا",
            "restart": "دوبارہ شروع",
        },
        "roman_urdu": {
            "title": "Box breathing",
            "intro": "4-count saans jo aapke nerves ko settle karne mein madad kar sakti hai.",
            "steps": [
                "Aaram se baithen. Shoulders soft rakhen.",
                "Naak se ahista 4 counts tak saans andar len.",
                "4 counts tak gently hold karein.",
                "Munh se ahista 4 counts tak saans bahar nikalen.",
                "Khali hold 4 counts. Agar acha lage to 3–4 rounds dohrayen.",
            ],
            "done": "Shaandaar. Ab body ko notice karein — thodi si sukoon bhi kaafi hai.",
            "next": "Next step",
            "finish": "I'm done",
            "restart": "Start over",
        },
    },
    "grounding_exercise": {
        "english": {
            "title": "5-4-3-2-1 grounding",
            "intro": "Name what you notice around you. This pulls attention gently into the present.",
            "steps": [
                "Name 5 things you can see.",
                "Name 4 things you can touch or feel.",
                "Name 3 things you can hear.",
                "Name 2 things you can smell (or remember smelling).",
                "Name 1 thing you can taste — or take a slow sip of water.",
            ],
            "done": "You're here, in this moment. That awareness is a form of care.",
            "next": "Next step",
            "finish": "I'm done",
            "restart": "Start over",
        },
        "urdu": {
            "title": "۵-۴-۳-۲-۱ گراؤنڈنگ",
            "intro": "اپنے ارد گرد جو محسوس ہو اسے نام دیں — توجہ حال میں آ جاتی ہے۔",
            "steps": [
                "پانچ چیزیں بتائیں جو آپ دیکھ سکتے ہیں۔",
                "چار چیزیں بتائیں جو آپ چھو سکتے ہیں یا محسوس کر سکتے ہیں۔",
                "تین آوازیں بتائیں جو آپ سن سکتے ہیں۔",
                "دو خوشبوئیں (یا یاد) بتائیں۔",
                "ایک ذائقہ بتائیں — یا آہستہ پانی کا گھونٹ لیں۔",
            ],
            "done": "آپ اس لمحے میں موجود ہیں۔ یہ توجہ بھی دیکھ بھال ہے۔",
            "next": "اگلا قدم",
            "finish": "میں نے مکمل کر لیا",
            "restart": "دوبارہ شروع",
        },
        "roman_urdu": {
            "title": "5-4-3-2-1 grounding",
            "intro": "Jo aap notice kar rahe hain usay naam dein — yeh attention present mein laata hai.",
            "steps": [
                "5 cheezein jo aap dekh sakte hain.",
                "4 cheezein jo aap touch/feel kar sakte hain.",
                "3 awazein jo aap sun sakte hain.",
                "2 khushboo (ya yaad).",
                "1 zaiqa — ya ahista paani ka ghoont.",
            ],
            "done": "Aap is lamhe mein hain. Yeh awareness bhi care hai.",
            "next": "Next step",
            "finish": "I'm done",
            "restart": "Start over",
        },
    },
    "journaling_prompt": {
        "english": {
            "title": "Gentle journal",
            "intro": "Write a few lines — no grammar rules, no judgment. Private to this session.",
            "prompt": "What's one feeling present right now, and what might it need from you?",
            "placeholder": "Start writing…",
            "save": "Save note",
            "saved": "Saved in this session. You can keep talking whenever you're ready.",
            "finish": "Close",
        },
        "urdu": {
            "title": "نرم جرنل",
            "intro": "چند سطریں لکھیں — کوئی اصول نہیں، کوئی فیصلہ نہیں۔ صرف اس نشست کے لیے۔",
            "prompt": "ابھی جو احساس ہے وہ کیا ہے، اور اسے آپ سے کیا چاہیے ہو سکتا ہے؟",
            "placeholder": "لکھنا شروع کریں…",
            "save": "نوٹ محفوظ کریں",
            "saved": "اس نشست میں محفوظ ہو گیا۔ جب تیار ہوں بات جاری رکھیں۔",
            "finish": "بند کریں",
        },
        "roman_urdu": {
            "title": "Gentle journal",
            "intro": "Chand lines likhen — koi rules nahi. Sirf is session ke liye.",
            "prompt": "Abhi konsa ehsaas hai, aur usay aapse kya chahiye ho sakta hai?",
            "placeholder": "Likhna shuru karein…",
            "save": "Save note",
            "saved": "Is session mein save ho gaya. Jab ready hon baat jari rakhen.",
            "finish": "Close",
        },
    },
}


def _lang_bucket(lang: str) -> str:
    if lang == "urdu":
        return "urdu"
    if lang == "roman_urdu":
        return "roman_urdu"
    return "english"


def get_coping_copy(action: str, lang: str) -> dict[str, Any]:
    bucket = _lang_bucket(lang)
    action_copy = _COPY.get(action, {})
    return action_copy.get(bucket) or action_copy.get("english") or {}


def start_coping(action: str) -> None:
    import streamlit as st

    if action not in COPING_ACTIONS:
        return
    st.session_state.active_coping = action
    st.session_state.coping_step = 0
    st.session_state.coping_completed = False


def render_coping_panel(lang: str) -> None:
    """Render the active coping exercise UI from session state."""
    import streamlit as st

    action = st.session_state.get("active_coping")
    if not action or action not in COPING_ACTIONS:
        return

    copy = get_coping_copy(action, lang)
    if not copy:
        return

    step = int(st.session_state.get("coping_step", 0))
    completed = bool(st.session_state.get("coping_completed", False))

    st.markdown('<div class="sakoon-coping-card">', unsafe_allow_html=True)
    st.markdown(f"### {copy['title']}")
    st.caption(copy["intro"])

    if action == "journaling_prompt":
        st.markdown(f"**{copy['prompt']}**")
        note = st.text_area(
            label="journal",
            value=st.session_state.get("journal_draft", ""),
            placeholder=copy["placeholder"],
            height=120,
            label_visibility="collapsed",
            key="journal_input_widget",
        )
        cols = st.columns([1, 1, 2])
        with cols[0]:
            if st.button(copy["save"], key="btn_journal_save", use_container_width=True):
                st.session_state.journal_draft = note
                notes = st.session_state.setdefault("journal_notes", [])
                if note and note.strip():
                    notes.append(note.strip())
                    try:
                        from sakoon.db import add_journal_entry

                        add_journal_entry(
                            body=note.strip(),
                            prompt=copy.get("prompt"),
                            session_id=st.session_state.get("db_session_id"),
                            user_id=st.session_state.get("db_user_id"),
                        )
                    except Exception:
                        st.session_state.db_error = True
                st.session_state.coping_completed = True
                st.rerun()
        with cols[1]:
            if st.button(copy["finish"], key="btn_journal_close", use_container_width=True):
                st.session_state.active_coping = None
                st.session_state.coping_step = 0
                st.session_state.coping_completed = False
                st.rerun()
        if st.session_state.get("coping_completed"):
            st.success(copy["saved"])
    else:
        steps: list[str] = copy.get("steps", [])
        if completed or step >= len(steps):
            from sakoon.core.security import escape_html

            st.markdown(
                f'<div class="sakoon-coping-step">{escape_html(copy["done"])}</div>',
                unsafe_allow_html=True,
            )
            cols = st.columns([1, 1, 2])
            with cols[0]:
                if st.button(copy["restart"], key="btn_coping_restart", use_container_width=True):
                    st.session_state.coping_step = 0
                    st.session_state.coping_completed = False
                    st.rerun()
            with cols[1]:
                if st.button(copy["finish"], key="btn_coping_finish", use_container_width=True):
                    st.session_state.active_coping = None
                    st.session_state.coping_step = 0
                    st.session_state.coping_completed = False
                    st.rerun()
        else:
            from sakoon.core.security import escape_html

            st.markdown(
                f'<div class="sakoon-coping-progress">Step {step + 1} of {len(steps)}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="sakoon-coping-step">{escape_html(steps[step])}</div>',
                unsafe_allow_html=True,
            )
            if st.button(copy["next"], key="btn_coping_next", type="primary"):
                nxt = step + 1
                st.session_state.coping_step = nxt
                if nxt >= len(steps):
                    st.session_state.coping_completed = True
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
