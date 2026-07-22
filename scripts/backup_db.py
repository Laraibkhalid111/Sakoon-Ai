#!/usr/bin/env python3
"""CLI: create a SQLite backup of sakoon.db."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sakoon.core.backup import backup_database, list_backups  # noqa: E402
from sakoon.core.config import get_settings  # noqa: E402
from sakoon.core.logging import setup_logging  # noqa: E402
from sakoon.core.paths import BACKUP_DIR  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Backup Sakoon SQLite database")
    parser.add_argument("--dir", type=Path, default=None, help="Backup directory")
    parser.add_argument("--keep", type=int, default=None, help="Number of backups to retain")
    parser.add_argument("--list", action="store_true", help="List existing backups and exit")
    args = parser.parse_args()

    setup_logging(get_settings().log_level)
    dest = args.dir or BACKUP_DIR
    keep = args.keep if args.keep is not None else get_settings().backup_keep

    if args.list:
        for p in list_backups(dest):
            print(p)
        return 0

    path = backup_database(dest_dir=dest, keep=keep)
    if path is None:
        print("Backup failed (see logs).", file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
