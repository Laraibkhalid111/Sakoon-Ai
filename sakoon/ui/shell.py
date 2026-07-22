"""Unified premium shell — view chrome, bilingual UI labels, layout class."""

from __future__ import annotations


def chrome_copy(lang: str) -> dict[str, str]:
    """Shared chrome strings (nav chrome, actions, sidebar) for EN / Urdu / Roman Urdu."""
    if lang == "urdu":
        return {
            "nav_label": "جائیں",
            "dark": "تاریک",
            "new_chat": "نئی گفتگو",
            "local_note": "مقامی نشست · ڈیٹا اسی ڈیوائس پر رہتا ہے",
            "voice": "آواز",
            "voice_hint": "اردو یا انگریزی میں بولیں — ویسپر سنبھال لے گا۔",
            "voice_paused": "ساکون کے جواب کے دوران آواز رک جاتی ہے…",
            "calming": "پرسکون مشقیں",
            "help_now": "ابھی مدد چاہیے؟",
            "history": "گفتگو کی تاریخ",
            "manage": "ترتیب",
            "rename": "نام تبدیل کریں",
            "rename_save": "محفوظ",
            "rename_placeholder": "گفتگو کا عنوان",
            "export_md": "ایکسپورٹ (.md)",
            "delete": "حذف",
            "delete_confirm": "حذف کی تصدیق",
            "deleted": "گفتگو حذف ہو گئی۔",
            "empty_history": "ابھی کوئی پرانی گفتگو نہیں۔",
            "open_chat": "کھولیں",
            "report": "رپورٹ اور ای میل",
            "generate_report": "رپورٹ بنائیں",
            "download_pdf": "پی ڈی ایف ڈاؤن لوڈ",
            "resend_email": "ای میل دوبارہ بھیجیں",
            "copy": "کاپی",
            "copied": "کاپی ہو گیا",
            "copy_failed": "ناکام",
            "regen": "دوبارہ",
            "regen_help": "جواب دوبارہ بنائیں",
            "latest": "↓ تازہ",
            "latest_help": "تازہ ترین پیغام پر جائیں",
            "disclaimer": (
                "ساکون AI پیشہ ورانہ ذہنی صحت کی دیکھ بھال کا متبادل نہیں۔ "
                "اگر آپ بحران میں ہیں تو لائسنس یافتہ پیشہ ور سے رابطہ کریں یا "
                "ہیلپ لائن پر کال کریں۔"
            ),
            "chat_eyebrow": "گفتگو",
            "chat_hint": "یہاں جو محسوس ہو رہا ہے، وہ لکھیں یا بولیں۔",
        }
    if lang == "roman_urdu":
        return {
            "nav_label": "Navigate",
            "dark": "Dark",
            "new_chat": "New chat",
            "local_note": "Local session · data isi device par rehta hai",
            "voice": "Voice",
            "voice_hint": "Urdu ya English mein bolain — Whisper sambhal lega.",
            "voice_paused": "Sakoon ke jawab ke dauran voice ruk jati hai…",
            "calming": "Calming exercises",
            "help_now": "Abhi madad chahiye?",
            "history": "Conversation history",
            "manage": "Manage",
            "rename": "Rename",
            "rename_save": "Save",
            "rename_placeholder": "Conversation title",
            "export_md": "Export (.md)",
            "delete": "Delete",
            "delete_confirm": "Confirm delete",
            "deleted": "Conversation deleted.",
            "empty_history": "No past conversations yet.",
            "open_chat": "Open",
            "report": "Report & email",
            "generate_report": "Generate Report",
            "download_pdf": "Download PDF",
            "resend_email": "Resend to Email",
            "copy": "Copy",
            "copied": "Copied",
            "copy_failed": "Failed",
            "regen": "Regen",
            "regen_help": "Regenerate reply",
            "latest": "↓ Latest",
            "latest_help": "Jump to latest message",
            "disclaimer": (
                "Sakoon AI professional mental health care ka badal nahi. "
                "Agar aap crisis mein hain to licensed professional se rabta karein "
                "ya helpline call karein."
            ),
            "chat_eyebrow": "Chat",
            "chat_hint": "Jo mehsoos ho raha hai, yahan likhein ya bolain.",
        }
    return {
        "nav_label": "Navigate",
        "dark": "Dark",
        "new_chat": "New chat",
        "local_note": "Local session · data stays on this device",
        "voice": "Voice",
        "voice_hint": "Speak in Urdu or English — Whisper handles the rest.",
        "voice_paused": "Voice pauses while Sakoon is replying…",
        "calming": "Calming exercises",
        "help_now": "Need help now?",
        "history": "Conversation history",
        "manage": "Manage",
        "rename": "Rename",
        "rename_save": "Save",
        "rename_placeholder": "Conversation title",
        "export_md": "Export (.md)",
        "delete": "Delete",
        "delete_confirm": "Confirm delete",
        "deleted": "Conversation deleted.",
        "empty_history": "No past conversations yet.",
        "open_chat": "Open",
        "report": "Report & email",
        "generate_report": "Generate Report",
        "download_pdf": "Download PDF",
        "resend_email": "Resend to Email",
        "copy": "Copy",
        "copied": "Copied",
        "copy_failed": "Failed",
        "regen": "Regen",
        "regen_help": "Regenerate reply",
        "latest": "↓ Latest",
        "latest_help": "Jump to latest message",
        "disclaimer": (
            "Sakoon AI is not a substitute for professional mental health care. "
            "If you are in crisis, please contact a licensed professional or call the helpline."
        ),
        "chat_eyebrow": "Chat",
        "chat_hint": "Type or speak whatever you're feeling — this is your space.",
    }


def shell_view_class(view: str) -> str:
    """CSS class for layout width / chat-first vs wide rooms."""
    if view == "wellness":
        return "sakoon-view-wellness"
    if view == "insights":
        return "sakoon-view-insights"
    return "sakoon-view-chat"


def render_chat_shell_intro(lang: str, message_count: int) -> None:
    """Soft Claude-style intro only while the welcome turn is alone."""
    import streamlit as st
    from sakoon.core.security import escape_html

    if message_count > 1:
        return
    copy = chrome_copy(lang)
    st.markdown(
        f'<div class="sakoon-chat-intro">'
        f'<p class="sakoon-chat-eyebrow">{escape_html(copy["chat_eyebrow"])}</p>'
        f'<p class="sakoon-chat-hint">{escape_html(copy["chat_hint"])}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )
