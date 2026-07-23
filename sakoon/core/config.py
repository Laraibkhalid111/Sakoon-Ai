"""
Central configuration — env / Streamlit secrets with safe defaults.
Never logs secret values.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*_args, **_kwargs):  # type: ignore[misc]
        return False

from sakoon.core.paths import ENV_FILE


def _secret(key: str, default: str | None = None) -> str | None:
    """Read from environment first, then st.secrets if available."""
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


def _clean_secret(value: str | None) -> str | None:
    """Strip whitespace/quotes; treat placeholders as missing."""
    if value is None:
        return None
    cleaned = value.strip().strip('"').strip("'").strip()
    if not cleaned:
        return None
    low = cleaned.lower()
    placeholders = {
        "your_groq_api_key_here",
        "your_api_key_here",
        "changeme",
        "xxx",
        "api_key",
        "groq_api_key",
        "replace_me",
    }
    if low in placeholders or low.startswith("your_") or "example" in low:
        return None
    return cleaned


@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None
    email_address: str | None
    email_app_password: str | None
    smtp_host: str
    smtp_port: int
    chat_model: str
    narrative_model: str
    whisper_model: str
    # Max user+assistant turns sent to Groq (system prompt is separate)
    max_history_messages: int
    log_level: str
    # Optional Fernet key (url-safe base64) for journal at-rest encryption
    encryption_key: str | None
    # Phase 6 ops
    rate_limit_chat_per_min: int
    rate_limit_auth_per_min: int
    backup_keep: int

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def has_smtp(self) -> bool:
        return bool(self.email_address and self.email_app_password)

    @property
    def has_encryption(self) -> bool:
        return bool(self.encryption_key)


def _int_secret(key: str, default: int, minimum: int = 0) -> int:
    raw = _secret(key, str(default)) or str(default)
    try:
        return max(minimum, int(raw))
    except ValueError:
        return default


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once per process. Call reload_settings() after env changes."""
    load_dotenv(ENV_FILE, override=True)
    port_raw = _secret("SMTP_PORT", "465") or "465"
    try:
        smtp_port = int(port_raw)
    except ValueError:
        smtp_port = 465

    hist_raw = _secret("MAX_HISTORY_MESSAGES", "24") or "24"
    try:
        max_hist = max(6, int(hist_raw))
    except ValueError:
        max_hist = 24

    return Settings(
        groq_api_key=_clean_secret(_secret("GROQ_API_KEY")),
        email_address=_clean_secret(_secret("EMAIL_ADDRESS")),
        email_app_password=_clean_secret(_secret("EMAIL_APP_PASSWORD")),
        smtp_host=_secret("SMTP_HOST", "smtp.gmail.com") or "smtp.gmail.com",
        smtp_port=smtp_port,
        chat_model=_secret("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile") or "llama-3.3-70b-versatile",
        narrative_model=_secret("GROQ_NARRATIVE_MODEL", "llama-3.1-8b-instant") or "llama-3.1-8b-instant",
        whisper_model=_secret("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo") or "whisper-large-v3-turbo",
        max_history_messages=max_hist,
        log_level=(_secret("LOG_LEVEL", "INFO") or "INFO").upper(),
        encryption_key=_clean_secret(_secret("ENCRYPTION_KEY")),
        rate_limit_chat_per_min=_int_secret("RATE_LIMIT_CHAT_PER_MIN", 20, minimum=1),
        rate_limit_auth_per_min=_int_secret("RATE_LIMIT_AUTH_PER_MIN", 10, minimum=1),
        backup_keep=_int_secret("BACKUP_KEEP", 14, minimum=1),
    )


def reload_settings() -> Settings:
    """Clear cache and reload (useful in tests)."""
    get_settings.cache_clear()
    return get_settings()


def settings_public_dict() -> dict[str, Any]:
    """Non-secret snapshot for health/debug panels."""
    s = get_settings()
    return {
        "has_groq": s.has_groq,
        "has_smtp": s.has_smtp,
        "has_encryption": s.has_encryption,
        "smtp_host": s.smtp_host,
        "smtp_port": s.smtp_port,
        "chat_model": s.chat_model,
        "narrative_model": s.narrative_model,
        "whisper_model": s.whisper_model,
        "max_history_messages": s.max_history_messages,
        "log_level": s.log_level,
        "rate_limit_chat_per_min": s.rate_limit_chat_per_min,
        "rate_limit_auth_per_min": s.rate_limit_auth_per_min,
        "backup_keep": s.backup_keep,
    }
