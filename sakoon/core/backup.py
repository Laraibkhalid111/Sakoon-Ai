"""SQLite backup helpers (Phase 6)."""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from sakoon.core.logging import get_logger
from sakoon.core.paths import BACKUP_DIR, DB_PATH

log = get_logger(__name__)


def backup_database(
    dest_dir: Path | None = None,
    keep: int = 14,
    source: Path | None = None,
) -> Path | None:
    """
    Create a consistent SQLite backup via the online backup API.
    Returns the backup file path, or None on failure.
    """
    src = Path(source or DB_PATH)
    out_dir = Path(dest_dir or BACKUP_DIR)
    try:
        if not src.exists():
            log.warning("backup skipped: database not found at %s", src)
            return None

        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        dest = out_dir / f"sakoon-{stamp}.db"

        src_conn = sqlite3.connect(str(src))
        try:
            dst_conn = sqlite3.connect(str(dest))
            try:
                src_conn.backup(dst_conn)
                dst_conn.commit()
            finally:
                dst_conn.close()
        finally:
            src_conn.close()

        _prune_old_backups(out_dir, keep=keep)
        log.info("event=db_backup path=%s keep=%s", dest, keep)
        return dest
    except Exception as e:
        log.error("backup_database failed: %s", e)
        return None


def _prune_old_backups(out_dir: Path, keep: int) -> None:
    if keep <= 0:
        return
    files = sorted(
        out_dir.glob("sakoon-*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old in files[keep:]:
        _safe_unlink(old)


def _safe_unlink(path: Path) -> None:
    for attempt in range(5):
        try:
            path.unlink()
            log.info("event=db_backup_pruned path=%s", path)
            return
        except OSError as e:
            if attempt == 4:
                log.warning("could not prune backup %s: %s", path, e)
            else:
                time.sleep(0.05 * (attempt + 1))


def list_backups(dest_dir: Path | None = None) -> list[Path]:
    out_dir = Path(dest_dir or BACKUP_DIR)
    if not out_dir.exists():
        return []
    return sorted(out_dir.glob("sakoon-*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
