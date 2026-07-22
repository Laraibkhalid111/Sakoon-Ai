"""Wellness content — affirmations and emergency resources (bilingual)."""

from __future__ import annotations

from datetime import date
from typing import Any


def _bucket(lang: str) -> str:
    if lang == "urdu":
        return "urdu"
    if lang == "roman_urdu":
        return "roman_urdu"
    return "english"


AFFIRMATIONS: dict[str, list[str]] = {
    "english": [
        "I can take this one moment at a time.",
        "My feelings are valid, and I am allowed to rest.",
        "I am doing the best I can with what I have today.",
        "Asking for help is a sign of strength.",
        "I deserve kindness — including from myself.",
        "This feeling will move. I can stay gentle while it does.",
        "I am safe enough to breathe and begin again.",
        "Small steps still count as progress.",
        "I can hold both struggle and hope at the same time.",
        "I am worthy of care and connection.",
    ],
    "urdu": [
        "میں ایک لمحہ ایک لمحہ لے کر آگے بڑھ سکتا/سکتی ہوں۔",
        "میرے احساسات درست ہیں، اور مجھے آرام کرنے کا حق ہے۔",
        "میں آج جو کچھ میرے پاس ہے اس سے بہترین کر رہا/رہی ہوں۔",
        "مدد مانگنا کمزوری نہیں، ہمت ہے۔",
        "میں مہربانی کا مستحق ہوں — خود سے بھی۔",
        "یہ احساس گزرے گا؛ میں نرم رہتے ہوئے انتظار کر سکتا/سکتی ہوں۔",
        "میں اتنا محفوظ ہوں کہ سانس لے سکوں اور دوبارہ شروع کر سکوں۔",
        "چھوٹے قدم بھی ترقی ہیں۔",
        "میں جدوجہد اور امید دونوں سنبھال سکتا/سکتی ہوں۔",
        "میں دیکھ بھال اور محبت کے لائق ہوں۔",
    ],
    "roman_urdu": [
        "Main ek lamha ek lamha le kar aage barh sakta/sakti hoon.",
        "Mere ehsaas valid hain, aur mujhe aaram karne ka haq hai.",
        "Main aaj jo mere paas hai us se best kar raha/rahi hoon.",
        "Madad mangna kamzori nahi, himmat hai.",
        "Main meharbani ka mustahiq hoon — khud se bhi.",
        "Yeh ehsaas guzrega; main narm rehte hue intezar kar sakta/sakti hoon.",
        "Main itna mehfooz hoon ke saans le sakoon aur dobara shuru kar sakoon.",
        "Chhote qadam bhi taraqqi hain.",
        "Main struggle aur umeed dono sambhal sakta/sakti hoon.",
        "Main dekhbhaal aur connection ke laiq hoon.",
    ],
}


def affirmation_for_today(lang: str = "english") -> str:
    """Deterministic daily affirmation (rotates by calendar day)."""
    bucket = _bucket(lang)
    items = AFFIRMATIONS.get(bucket) or AFFIRMATIONS["english"]
    idx = date.today().toordinal() % len(items)
    return items[idx]


def list_affirmations(lang: str = "english") -> list[str]:
    bucket = _bucket(lang)
    return list(AFFIRMATIONS.get(bucket) or AFFIRMATIONS["english"])


# Emergency / support resources — trusted static content for Pakistan + general
EMERGENCY_RESOURCES: dict[str, list[dict[str, str]]] = {
    "english": [
        {
            "name": "Umang Mental Health Helpline (Pakistan)",
            "detail": "0311-7786264 — free mental health support line",
            "when": "Distress, anxiety, suicidal thoughts, or need to talk now",
        },
        {
            "name": "Local emergency services",
            "detail": "Call your local emergency number immediately",
            "when": "Immediate danger to yourself or someone else",
        },
        {
            "name": "Trusted person",
            "detail": "A friend, family member, or neighbour who can stay with you",
            "when": "You feel unsafe alone or need presence more than advice",
        },
        {
            "name": "Licensed counsellor / psychiatrist",
            "detail": "Professional care for ongoing symptoms",
            "when": "Struggles lasting 2+ weeks, or daily life is heavily affected",
        },
    ],
    "urdu": [
        {
            "name": "امنگ مینٹل ہیلتھ ہیلپ لائن (پاکستان)",
            "detail": "0311-7786264 — مفت ذہنی صحت کی مدد",
            "when": "پریشانی، اضطراب، خودکشی کے خیالات، یا ابھی بات کی ضرورت",
        },
        {
            "name": "مقامی ایمرجنسی خدمات",
            "detail": "فوراً اپنے قریبی ایمرجنسی نمبر پر کال کریں",
            "when": "خود یا کسی اور کو فوری خطرہ ہو",
        },
        {
            "name": "قابلِ اعتماد شخص",
            "detail": "دوست، خاندان، یا پڑوسی جو آپ کے ساتھ رہ سکے",
            "when": "اکیلے محسوس کرنا خطرناک لگے یا موجودگی چاہیے ہو",
        },
        {
            "name": "لائسنس یافتہ کونسلر / سائیکاٹرسٹ",
            "detail": "جاری علامات کے لیے پیشہ ورانہ دیکھ بھال",
            "when": "دو ہفتوں سے زیادہ جدوجہد، یا روزمرہ زندگی متاثر ہو",
        },
    ],
    "roman_urdu": [
        {
            "name": "Umang Mental Health Helpline (Pakistan)",
            "detail": "0311-7786264 — muft mental health support",
            "when": "Distress, anxiety, suicidal thoughts, ya abhi baat karni ho",
        },
        {
            "name": "Local emergency services",
            "detail": "Apna local emergency number foran call karein",
            "when": "Khud ya kisi aur ko fori khatra ho",
        },
        {
            "name": "Trusted person",
            "detail": "Dost, family, ya neighbour jo aapke saath reh sake",
            "when": "Akele feel karna khatarnak lage ya presence chahiye ho",
        },
        {
            "name": "Licensed counsellor / psychiatrist",
            "detail": "Ongoing symptoms ke liye professional care",
            "when": "2+ hafton se struggle, ya daily life bohot asar andaz ho",
        },
    ],
}


def emergency_resources(lang: str = "english") -> list[dict[str, str]]:
    bucket = _bucket(lang)
    return list(EMERGENCY_RESOURCES.get(bucket) or EMERGENCY_RESOURCES["english"])


def mood_label(rating: int, lang: str = "english") -> str:
    """Short human label for a 1–10 mood rating."""
    r = max(1, min(10, int(rating)))
    if lang == "urdu":
        if r <= 3:
            return "بہت مشکل"
        if r <= 5:
            return "بھاری"
        if r <= 7:
            return "ٹھیک ٹھاک"
        return "ہلکا / مستحکم"
    if lang == "roman_urdu":
        if r <= 3:
            return "bohot mushkil"
        if r <= 5:
            return "bhaari"
        if r <= 7:
            return "theek thaak"
        return "halka / mustaqil"
    if r <= 3:
        return "Very hard"
    if r <= 5:
        return "Heavy"
    if r <= 7:
        return "Okay-ish"
    return "Lighter / steadier"


def wellness_ui_copy(lang: str) -> dict[str, Any]:
    """Labels for the wellness view."""
    if lang == "urdu":
        return {
            "nav_chat": "گفتگو",
            "nav_wellness": "فلاحی کمرہ",
            "title": "آپ کا فلاحی کمرہ",
            "subtitle": "مزاج، جرنل، اثبات، اور ہنگامی وسائل — سب ایک جگہ۔",
            "tab_mood": "مزاج",
            "tab_journal": "جرنل",
            "tab_affirm": "اثبات",
            "tab_resources": "مدد",
            "tab_exercises": "مشقیں",
            "mood_prompt": "آج آپ کا مزاج ۱ سے ۱۰؟",
            "mood_note": "اختیاری نوٹ",
            "mood_save": "مزاج محفوظ کریں",
            "mood_saved": "مزاج محفوظ ہو گیا۔",
            "mood_history": "حالیہ مزاج",
            "journal_prompt": "آج آپ کیا محسوس کر رہے ہیں؟",
            "journal_placeholder": "یہاں لکھیں…",
            "journal_save": "جرنل محفوظ کریں",
            "journal_saved": "جرنل محفوظ ہو گیا۔",
            "journal_history": "حالیہ اندراجات",
            "affirm_today": "آج کا اثبات",
            "affirm_more": "مزید اثبات",
            "resources_title": "ہنگامی اور سپورٹ وسائل",
            "resources_note": "ساکون طبی ایمرجنسی سروس نہیں ہے۔ خطرے میں فوری مدد لیں۔",
            "exercises_hint": "سانس، گراؤنڈنگ، یا جرنل شروع کریں۔",
            "empty": "ابھی کچھ محفوظ نہیں۔",
            "when": "کب:",
        }
    if lang == "roman_urdu":
        return {
            "nav_chat": "Chat",
            "nav_wellness": "Wellness",
            "title": "Aapka wellness room",
            "subtitle": "Mood, journal, affirmations, aur emergency resources — ek jagah.",
            "tab_mood": "Mood",
            "tab_journal": "Journal",
            "tab_affirm": "Affirmations",
            "tab_resources": "Help",
            "tab_exercises": "Exercises",
            "mood_prompt": "Aaj aapka mood 1 se 10?",
            "mood_note": "Optional note",
            "mood_save": "Save mood",
            "mood_saved": "Mood save ho gaya.",
            "mood_history": "Recent moods",
            "journal_prompt": "Aaj aap kya mehsoos kar rahe hain?",
            "journal_placeholder": "Yahan likhen…",
            "journal_save": "Save journal",
            "journal_saved": "Journal save ho gaya.",
            "journal_history": "Recent entries",
            "affirm_today": "Aaj ki affirmation",
            "affirm_more": "Aur affirmations",
            "resources_title": "Emergency aur support resources",
            "resources_note": "Sakoon medical emergency service nahi hai. Khatre mein fori madad len.",
            "exercises_hint": "Breathing, grounding, ya journal shuru karein.",
            "empty": "Abhi kuch save nahi hua.",
            "when": "Kab:",
        }
    return {
        "nav_chat": "Chat",
        "nav_wellness": "Wellness",
        "title": "Your wellness room",
        "subtitle": "Mood, journal, affirmations, and emergency support — in one calm place.",
        "tab_mood": "Mood",
        "tab_journal": "Journal",
        "tab_affirm": "Affirmations",
        "tab_resources": "Help now",
        "tab_exercises": "Exercises",
        "mood_prompt": "How is your mood from 1 to 10 today?",
        "mood_note": "Optional note",
        "mood_save": "Save mood",
        "mood_saved": "Mood saved.",
        "mood_history": "Recent moods",
        "journal_prompt": "What's on your mind right now?",
        "journal_placeholder": "Write here…",
        "journal_save": "Save journal",
        "journal_saved": "Journal entry saved.",
        "journal_history": "Recent entries",
        "affirm_today": "Today's affirmation",
        "affirm_more": "More affirmations",
        "resources_title": "Emergency & support resources",
        "resources_note": "Sakoon is not an emergency service. If you're in danger, get help immediately.",
        "exercises_hint": "Start breathing, grounding, or a short journal.",
        "empty": "Nothing saved yet.",
        "when": "When:",
    }
