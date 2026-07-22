"""Optional at-rest encryption for journal bodies (Fernet)."""

from __future__ import annotations

_PREFIX = "enc:v1:"


def _fernet():
    from sakoon.core.config import get_settings

    key = get_settings().encryption_key
    if not key:
        return None
    try:
        from cryptography.fernet import Fernet

        return Fernet(key.encode("utf-8") if isinstance(key, str) else key)
    except Exception:
        return None


def encrypt_text(plain: str) -> str:
    """Encrypt plaintext when ENCRYPTION_KEY is configured; otherwise return as-is."""
    if not plain:
        return plain
    f = _fernet()
    if f is None:
        return plain
    token = f.encrypt(plain.encode("utf-8")).decode("utf-8")
    return f"{_PREFIX}{token}"


def decrypt_text(stored: str) -> str:
    """Decrypt values produced by encrypt_text; pass through plaintext."""
    if not stored:
        return stored
    if not stored.startswith(_PREFIX):
        return stored
    f = _fernet()
    if f is None:
        return stored  # key missing — return ciphertext rather than crashing
    try:
        raw = stored[len(_PREFIX):].encode("utf-8")
        return f.decrypt(raw).decode("utf-8")
    except Exception:
        return stored
