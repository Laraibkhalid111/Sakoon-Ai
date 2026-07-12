"""
database.py — Sakoon AI
SQLite persistence layer (sakoon.db). Implements schema creation for the
4 flat tables (users, sessions, messages, symptom_snapshots) and all CRUD
helpers called by app.py per conversation turn. Zero external dependencies
beyond Python's built-in sqlite3 module.
"""
# Logic implemented in M3
