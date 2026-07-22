"""Project path constants — always resolve from the repository root."""

from __future__ import annotations

import os
from pathlib import Path

# sakoon/core/paths.py → parents[0]=core, [1]=sakoon, [2]=repo root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _data_dir() -> Path:
    """Writable data root (DB + backups). Override with DATA_DIR for Docker."""
    raw = (os.getenv("DATA_DIR") or "").strip()
    if raw:
        return Path(raw)
    return PROJECT_ROOT


DATA_DIR = _data_dir()
DB_PATH = DATA_DIR / "sakoon.db"
BACKUP_DIR = DATA_DIR / "backups"
FONT_URDU = PROJECT_ROOT / "NotoNastaliqUrdu-Regular.ttf"
ENV_FILE = PROJECT_ROOT / ".env"
