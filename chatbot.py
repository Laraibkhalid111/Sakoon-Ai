"""
chatbot.py — Sakoon AI
Groq API client wrapper. Provides a single public function `get_ai_response()`
that takes the full conversation history and the current session profile,
calls Groq with JSON mode enabled, parses and validates the response
(with fallback defaults so a malformed response never crashes the app),
and returns a fully-formed response dict.

Also provides `generate_report_narrative()` for the PDF summary paragraph.
"""

import json
import re
import streamlit as st
from groq import Groq

from prompts import (
    SYSTEM_PROMPT,
    REPORT_NARRATIVE_PROMPT,
    OFF_TOPIC_REDIRECT,
    WELCOME_MESSAGE,
)

# ---------------------------------------------------------------------------
# Groq client — initialised lazily so import doesn't crash if key is missing
# ---------------------------------------------------------------------------

_client: Groq | None = None


def _get_client() -> Groq:
    """Return (or lazily create) the Groq client, reading key from st.secrets."""
    global _client
    if _client is None:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except (KeyError, FileNotFoundError):
            # Fallback for local dev using python-dotenv / .env
            import os
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set. Check .streamlit/secrets.toml or .env")
        _client = Groq(api_key=api_key)
    return _client


# ---------------------------------------------------------------------------
# Default/fallback response shape (used when JSON parse fails)
# ---------------------------------------------------------------------------

def _default_response(lang: str = "english") -> dict:
    """Return a safe default response that won't crash the app."""
    return {
        "reply_to_user": (
            "I'm having a little trouble responding right now. "
            "Give me a moment and try again."
            if lang == "english"
            else "مجھے ابھی جواب دینے میں تھوڑی مشکل ہو رہی ہے۔ ذرا رکیں اور دوبارہ کوشش کریں۔"
        ),
        "conversation_stage": "check_in",
        "detected_language": lang,
        "extracted": {
            "name": None,
            "email": None,
            "phone": None,
            "primary_concern": None,
            "mood_rating": None,
            "symptoms": [],
            "possible_triggers": [],
            "risk_flags": [],
        },
        "suggested_coping_action": "none",
        "is_on_topic": True,
        "_error": True,  # flag so app.py can show the error banner
    }


# ---------------------------------------------------------------------------
# Response validation & sanitisation
# ---------------------------------------------------------------------------

_VALID_STAGES = {
    "greeting", "building_rapport", "symptom_exploration",
    "root_cause", "recovery_planning", "check_in",
    "closing", "off_topic_redirect", "crisis",
}
_VALID_LANGUAGES = {"urdu", "english", "roman_urdu", "mixed"}
_VALID_COPING = {"grounding_exercise", "breathing_exercise", "journaling_prompt", "none"}


def _validate_and_fix(data: dict) -> dict:
    """
    Clamp/coerce any out-of-range values so a slightly-off model response
    never crashes the app downstream.
    """
    if not isinstance(data.get("reply_to_user"), str):
        data["reply_to_user"] = "..."
    if data.get("conversation_stage") not in _VALID_STAGES:
        data["conversation_stage"] = "check_in"
    if data.get("detected_language") not in _VALID_LANGUAGES:
        data["detected_language"] = "english"
    if data.get("suggested_coping_action") not in _VALID_COPING:
        data["suggested_coping_action"] = "none"
    if not isinstance(data.get("is_on_topic"), bool):
        data["is_on_topic"] = True

    ext = data.get("extracted")
    if not isinstance(ext, dict):
        ext = {}
    # Ensure list fields are lists
    for field in ("symptoms", "possible_triggers", "risk_flags"):
        if not isinstance(ext.get(field), list):
            ext[field] = []
    # Clamp mood_rating to 1-10 int or None
    mr = ext.get("mood_rating")
    if mr is not None:
        try:
            mr = max(1, min(10, int(mr)))
        except (ValueError, TypeError):
            mr = None
    ext["mood_rating"] = mr
    data["extracted"] = ext
    return data


def _parse_json_response(raw: str) -> dict | None:
    """
    Try to parse raw string as JSON. Handles the case where the model wraps
    the JSON in markdown code fences despite being told not to.
    """
    raw = raw.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract the first {...} block
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def get_ai_response(
    conversation_history: list[dict],
    current_lang: str = "english",
) -> dict:
    """
    Send the conversation history to Groq with JSON mode and return a
    validated response dict.

    Args:
        conversation_history: List of {"role": "user"|"assistant", "content": str}
            dicts — the full chat so far, NOT including the system message.
        current_lang: Best guess at the user's current language ("english" |
            "urdu" | "roman_urdu" | "mixed") for fallback copy selection.

    Returns:
        A dict with keys: reply_to_user, conversation_stage, detected_language,
        extracted, suggested_coping_action, is_on_topic.
        May also contain "_error": True if the call failed.
    """
    client = _get_client()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_history,
    ]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1024,
        )
        raw = completion.choices[0].message.content or ""
        data = _parse_json_response(raw)
        if data is None:
            return _default_response(current_lang)
        return _validate_and_fix(data)

    except Exception:
        # Catches Groq API errors, network timeouts, auth errors, etc.
        return _default_response(current_lang)


# ---------------------------------------------------------------------------
# Report narrative — single focused call (plain text, not JSON mode)
# ---------------------------------------------------------------------------

def generate_report_narrative(session_data: dict) -> str:
    """
    Generate a one-paragraph plain-language narrative for the PDF report.
    Returns the paragraph as a plain string.
    On failure, returns a generic placeholder so PDF generation never crashes.
    """
    try:
        client = _get_client()
        prompt = REPORT_NARRATIVE_PROMPT.format(
            session_data=json.dumps(session_data, ensure_ascii=False, indent=2)
        )
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # lighter model for this simple task
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300,
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return (
            "During this session, the user shared their feelings and experiences. "
            "A full summary could not be generated at this time."
        )


# ---------------------------------------------------------------------------
# Whisper transcription — voice input pipeline (M4)
# ---------------------------------------------------------------------------

def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str | None:
    """
    Send raw audio bytes to Groq Whisper (whisper-large-v3-turbo) and return
    the transcription as a plain string, or None on any failure.

    Handles: silence/empty audio, API errors, network timeouts, auth issues.
    Never raises — the caller shows the warning banner copy from DESIGN.md §6.5.

    Args:
        audio_bytes: Raw audio file bytes from st.audio_input().
        filename: Filename hint for the Groq API (affects MIME type detection).

    Returns:
        Transcribed text string, or None on failure / empty result.
    """
    if not audio_bytes:
        return None
    try:
        client = _get_client()
        # Groq Whisper expects a file-like object with a name attribute
        import io
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            response_format="text",
        )
        # response_format="text" returns a plain string (not an object)
        text = transcription.strip() if isinstance(transcription, str) else (transcription.text or "").strip()
        # Treat very short or empty transcriptions as silence/failure
        if not text or len(text) < 2:
            return None
        return text
    except Exception:
        return None
