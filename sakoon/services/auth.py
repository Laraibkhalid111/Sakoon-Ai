"""Authentication service — bcrypt register / login (Phase 5)."""

from __future__ import annotations

import re
from typing import Any

from sakoon.core.logging import get_logger
from sakoon.db import create_auth_user, get_user_by_username

log = get_logger(__name__)

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


def hash_password(password: str) -> str:
    import bcrypt

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    import bcrypt

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except Exception:
        return False


def validate_username(username: str) -> tuple[bool, str]:
    uname = (username or "").strip()
    if not _USERNAME_RE.match(uname):
        return False, "Username must be 3–32 characters (letters, numbers, underscore)."
    return True, uname.lower()


def validate_password(password: str) -> tuple[bool, str]:
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters."
    if len(password) > 128:
        return False, "Password is too long."
    return True, password


def register_user(
    username: str,
    password: str,
    name: str | None = None,
    email: str | None = None,
    preferred_language: str = "english",
) -> tuple[bool, str, int | None]:
    """
    Register a new account.
    Returns (ok, message, user_id).
    """
    ok_u, uname_or_err = validate_username(username)
    if not ok_u:
        return False, uname_or_err, None
    ok_p, pwd_or_err = validate_password(password)
    if not ok_p:
        return False, pwd_or_err, None

    if get_user_by_username(uname_or_err):
        return False, "That username is already taken.", None

    pwd_hash = hash_password(pwd_or_err)
    uid = create_auth_user(
        username=uname_or_err,
        password_hash=pwd_hash,
        name=(name or "").strip() or None,
        email=(email or "").strip() or None,
        preferred_language=preferred_language,
    )
    if uid is None:
        return False, "Could not create account. Try a different username.", None
    log.info("Registered user id=%s username=%s", uid, uname_or_err)
    return True, "Account created. You can sign in now.", uid


def authenticate(username: str, password: str) -> tuple[bool, str, dict[str, Any] | None]:
    """
    Verify credentials.
    Returns (ok, message, public_user_dict without password_hash).
    """
    ok_u, uname_or_err = validate_username(username)
    if not ok_u:
        return False, "Invalid username or password.", None
    if not password:
        return False, "Invalid username or password.", None

    row = get_user_by_username(uname_or_err)
    if not row or not row.get("password_hash"):
        return False, "Invalid username or password.", None
    if not verify_password(password, row["password_hash"]):
        return False, "Invalid username or password.", None

    public = {
        "id": int(row["id"]),
        "username": row.get("username"),
        "name": row.get("name"),
        "email": row.get("email"),
        "preferred_language": row.get("preferred_language") or "english",
    }
    return True, "Signed in.", public
