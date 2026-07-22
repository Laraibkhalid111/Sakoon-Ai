"""Backward-compatible shim — implementation lives in sakoon.services.chatbot """
from sakoon.services.chatbot import (  # noqa: F401
    get_ai_response,
    generate_report_narrative,
    transcribe_audio,
    truncate_history,
    _validate_and_fix,
    _parse_json_response,
)
