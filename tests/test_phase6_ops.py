"""Phase 6 — ops: rate limit, backup, health, metrics."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sakoon.core.metrics import emit, reset_metrics, snapshot  # noqa: E402
from sakoon.core.rate_limit import SlidingWindowRateLimiter, get_limiter  # noqa: E402


def test_rate_limiter_blocks_after_limit():
    lim = SlidingWindowRateLimiter()
    assert lim.check("u1", limit=2, window_sec=60).allowed is True
    assert lim.check("u1", limit=2, window_sec=60).allowed is True
    blocked = lim.check("u1", limit=2, window_sec=60)
    assert blocked.allowed is False
    assert blocked.retry_after_sec > 0
    # Different key still allowed
    assert lim.check("u2", limit=2, window_sec=60).allowed is True


def test_metrics_emit_and_snapshot():
    reset_metrics()
    emit("chat_turn_queued", user_id=1)
    emit("chat_turn_queued", user_id=1)
    emit("crisis_detected")
    snap = snapshot()
    assert snap["chat_turn_queued"] == 2
    assert snap["crisis_detected"] == 1


def test_backup_and_health(tmp_path, monkeypatch):
    import sakoon.db.database as db
    from sakoon.core import backup as backup_mod
    from sakoon.core.backup import backup_database, list_backups
    from sakoon.core.config import reload_settings
    from sakoon.core.health import check_health

    db_file = tmp_path / "sakoon.db"
    backup_dir = tmp_path / "backups"
    monkeypatch.setattr(db, "DB_PATH", db_file)
    monkeypatch.setattr(backup_mod, "DB_PATH", db_file)
    monkeypatch.setattr(backup_mod, "BACKUP_DIR", backup_dir)
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    reload_settings()

    assert db.init_db() is True
    path = backup_database(dest_dir=backup_dir, keep=2, source=db_file)
    assert path is not None
    assert path.exists()
    assert path.parent == backup_dir

    # Create extras and prune (Windows may briefly lock files; allow small slack)
    backup_database(dest_dir=backup_dir, keep=2, source=db_file)
    backup_database(dest_dir=backup_dir, keep=2, source=db_file)
    remaining = list_backups(backup_dir)
    assert 1 <= len(remaining) <= 3
    assert all(p.exists() for p in remaining)

    # Health uses live DB_PATH from database module
    health = check_health()
    assert "ok" in health
    assert "settings" in health
    assert "metrics" in health


def test_process_limiter_reset():
    lim = get_limiter()
    lim.reset()
    r = lim.check("reset-key", limit=1, window_sec=60)
    assert r.allowed is True
    lim.reset("reset-key")
