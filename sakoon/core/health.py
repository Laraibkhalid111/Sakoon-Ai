"""Health status for ops / Docker / debug panels (Phase 6)."""

from __future__ import annotations

from typing import Any

from sakoon.core.config import settings_public_dict
from sakoon.core.metrics import snapshot as metrics_snapshot
from sakoon.core.paths import BACKUP_DIR, DATA_DIR, DB_PATH


def check_health() -> dict[str, Any]:
    """
    Return a non-secret health payload.
    `ok` is True when the app can persist data (DB path writable / openable).
    """
    db_ok, db_detail = _probe_db()
    settings = settings_public_dict()
    return {
        "ok": db_ok,
        "service": "sakoon-ai",
        "db": {"ok": db_ok, "detail": db_detail, "path": str(DB_PATH)},
        "paths": {
            "data_dir": str(DATA_DIR),
            "backup_dir": str(BACKUP_DIR),
        },
        "settings": settings,
        "metrics": metrics_snapshot(),
    }


def _probe_db() -> tuple[bool, str]:
    try:
        from sakoon.db.database import init_db, _connect

        if not init_db():
            return False, "init_db failed"
        with _connect() as conn:
            conn.execute("SELECT 1").fetchone()
        return True, "ok"
    except Exception as e:
        return False, str(e)
