"""Input validation helpers shared by the chat orchestration layer."""

from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\+?\d{10,13}$")


def validate_name(value: str | None) -> tuple[bool, str | None]:
    """Return (ok, cleaned). Digits-only names are rejected."""
    if value is None:
        return True, None
    cleaned = value.strip()
    if not cleaned or cleaned.isdigit():
        return False, None
    return True, cleaned


def validate_email(value: str | None) -> tuple[bool, str | None]:
    if value is None:
        return True, None
    cleaned = value.strip()
    if not _EMAIL_RE.match(cleaned):
        return False, None
    return True, cleaned


def validate_phone(value: str | None) -> tuple[bool, str | None]:
    if value is None:
        return True, None
    cleaned = value.strip().replace(" ", "").replace("-", "")
    if not _PHONE_RE.match(cleaned):
        return False, None
    return True, cleaned
