"""
sakoon.services.chatbot — Groq LLM + Whisper wrapper.

Public API:
  get_ai_response(), generate_report_narrative(), transcribe_audio()
  _validate_and_fix(), _parse_json_response()  (exported for tests)
"""

from __future__ import annotations

import io
import json
import re

from groq import Groq

from sakoon.core.config import get_settings
from sakoon.core.logging import get_logger
from sakoon.services.prompts import REPORT_NARRATIVE_PROMPT, SYSTEM_PROMPT

log = get_logger(__name__)

_VALID_STAGES = {
    "greeting", "building_rapport", "symptom_exploration",
    "root_cause", "recovery_planning", "check_in",
    "closing", "off_topic_redirect", "crisis",
}
_VALID_LANGUAGES = {"urdu", "english", "roman_urdu", "mixed"}
_VALID_COPING = {"grounding_exercise", "breathing_exercise", "journaling_prompt", "none"}


def _get_client() -> Groq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not set. Check .env or .streamlit/secrets.toml")
    return Groq(api_key=settings.groq_api_key)


def truncate_history(conversation_history: list[dict], max_messages: int | None = None) -> list[dict]:
    """
    Keep the most recent N messages for the Groq call.
    Always preserves message order. Never mutates the input list.
    """
    limit = max_messages if max_messages is not None else get_settings().max_history_messages
    if limit <= 0 or len(conversation_history) <= limit:
        return list(conversation_history)
    return list(conversation_history[-limit:])


def _default_response(lang: str = "english") -> dict:
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
        "_error": True,
    }


def _validate_and_fix(data: dict) -> dict:
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
    for field in ("symptoms", "possible_triggers", "risk_flags"):
        if not isinstance(ext.get(field), list):
            ext[field] = []
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
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


def get_ai_response(
    conversation_history: list[dict],
    current_lang: str = "english",
) -> dict:
    """
    Send (truncated) conversation history to Groq JSON mode and return a
    validated response dict. On failure returns _default_response with _error.
    """
    settings = get_settings()
    history = truncate_history(conversation_history, settings.max_history_messages)
    if len(conversation_history) > len(history):
        log.info(
            "Truncated Groq history from %s to %s messages",
            len(conversation_history),
            len(history),
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
    ]

    try:
        client = _get_client()
        completion = client.chat.completions.create(
            model=settings.chat_model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1024,
        )
        raw = completion.choices[0].message.content or ""
        data = _parse_json_response(raw)
        if data is None:
            log.error("Groq returned unparseable JSON (len=%s)", len(raw))
            return _default_response(current_lang)
        return _validate_and_fix(data)

    except Exception as exc:
        log.error("get_ai_response failed: %s", type(exc).__name__)
        return _default_response(current_lang)


def generate_report_narrative(session_data: dict) -> str:
    settings = get_settings()
    try:
        client = _get_client()
        prompt = REPORT_NARRATIVE_PROMPT.format(
            session_data=json.dumps(session_data, ensure_ascii=False, indent=2)
        )
        completion = client.chat.completions.create(
            model=settings.narrative_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300,
        )
        return (completion.choices[0].message.content or "").strip()
    except Exception as exc:
        log.error("generate_report_narrative failed: %s", type(exc).__name__)
        return (
            "During this session, the user shared their feelings and experiences. "
            "A full summary could not be generated at this time."
        )


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str | None:
    if not audio_bytes:
        return None
    settings = get_settings()
    try:
        client = _get_client()
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        transcription = client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
            response_format="text",
        )
        text = (
            transcription.strip()
            if isinstance(transcription, str)
            else (transcription.text or "").strip()
        )
        if not text or len(text) < 2:
            return None
        return text
    except Exception as exc:
        log.error("transcribe_audio failed: %s", type(exc).__name__)
        return None
