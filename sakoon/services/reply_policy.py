"""Pure reply / profile merge helpers (testable without Streamlit)."""

from __future__ import annotations

from typing import Any, Callable


def apply_language_from_response(
    detected: str,
    override: str = "Auto",
) -> str:
    """Resolve effective UI language from model detection + sidebar override."""
    if override == "English":
        return "english"
    if override == "اردو":
        return "urdu"
    return detected or "english"


def merge_extracted_fields(
    profile: dict[str, Any],
    extracted: dict[str, Any],
    *,
    validate_name: Callable,
    validate_email: Callable,
    validate_phone: Callable,
) -> tuple[dict[str, Any], bool, bool, bool, int | None]:
    """
    Merge model-extracted contact/mood fields into profile.
    Returns (profile, valid_name, valid_email, valid_phone, mood_changed_to).
    mood_changed_to is the new rating when mood changed, else None.
    """
    ext = extracted or {}
    mood_changed_to: int | None = None

    valid_name, name_val = validate_name(ext.get("name"))
    if valid_name and name_val:
        profile["name"] = name_val
    elif ext.get("name"):
        valid_name = False
    else:
        valid_name = True

    valid_email, email_val = validate_email(ext.get("email"))
    if valid_email and email_val:
        profile["email"] = email_val
    elif ext.get("email"):
        valid_email = False
    else:
        valid_email = True

    valid_phone, phone_val = validate_phone(ext.get("phone"))
    if valid_phone and phone_val:
        profile["phone"] = phone_val
    elif ext.get("phone"):
        valid_phone = False
    else:
        valid_phone = True

    if ext.get("primary_concern"):
        profile["primary_concern"] = ext["primary_concern"]

    if ext.get("mood_rating") is not None:
        mood_changed_to = ext["mood_rating"]
        profile["mood_rating"] = mood_changed_to

    for list_field in ("symptoms", "possible_triggers", "risk_flags"):
        existing = profile.get(list_field, []) or []
        new_items = ext.get(list_field, []) or []
        profile[list_field] = list(dict.fromkeys(existing + new_items))

    return profile, valid_name, valid_email, valid_phone, mood_changed_to


def choose_assistant_reply(
    response: dict[str, Any],
    lang: str,
    *,
    valid_name: bool,
    valid_email: bool,
    valid_phone: bool,
    redirect_copy: str,
) -> tuple[str, bool]:
    """
    Pick final user-facing reply + redirect flag (off-topic / validation).
    """
    if not response.get("is_on_topic", True):
        return redirect_copy, True
    if not valid_name:
        if lang == "urdu":
            return "مجھے آپ کا نام سمجھ نہیں آیا — میں آپ کو کیا کہہ کر بلاؤں؟", False
        return "I didn't quite catch your name — what should I call you?", False
    if not valid_email:
        if lang == "urdu":
            return "یہ مکمل ای میل نہیں لگ رہی — ایک بار دوبارہ چیک کر لیں؟", False
        return "That doesn't look like a complete email — mind double-checking it?", False
    if not valid_phone:
        if lang == "urdu":
            return "براہ کرم اپنا نمبر کوڈ کے ساتھ لکھیں، مثلاً +923001234567", False
        return "Could you share your number with the country code, like +923001234567?", False
    return response.get("reply_to_user", "...") or "...", False


def rate_limit_message(lang: str, wait_s: int) -> str:
    if lang == "urdu":
        return f"آپ تھوڑے تیزی سے پیغام بھیج رہے ہیں۔ براہِ کرم تقریباً {wait_s} سیکنڈ انتظار کریں۔"
    return (
        f"You're sending messages a bit quickly. Please wait about {wait_s} seconds, then try again."
    )


def avatar_initials(name: str | None) -> str:
    cleaned = (name or "You").strip()
    parts = cleaned.replace("_", " ").split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return (cleaned[:2] if len(cleaned) > 1 else cleaned[:1] or "Y").upper()
