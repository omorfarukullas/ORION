"""
database/database.py
====================
STUB — Phase 11

SQLite persistence layer for ORION's long-term memory.
Stores command history, user-defined memories ("my project folder is…"),
and preferences.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any


class Database:
    """
    SQLite wrapper for ORION's persistent storage.

    Tables (Phase 11):
        - command_history  : raw_text, intent, entities, timestamp, outcome
        - memories         : key (str), value (str), created_at, updated_at
        - preferences      : key (str), value (str)

    Uses stdlib sqlite3 — no extra dependency.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._conn = None

    def connect(self) -> None:
        """Open (or create) the SQLite database and create tables."""
        raise NotImplementedError("Database is implemented in Phase 11.")

    def log_command(self, raw_text: str, intent: str, outcome: str) -> None:
        """Persist a command and its outcome to command_history."""
        raise NotImplementedError("Database is implemented in Phase 11.")

    def save_memory(self, key: str, value: str) -> None:
        """Store a user-defined memory, e.g. 'project_folder' → 'Desktop/AI'."""
        raise NotImplementedError("Database is implemented in Phase 11.")

    def recall_memory(self, key: str) -> Any:
        """Retrieve a stored memory value by key, or None if not found."""
        raise NotImplementedError("Database is implemented in Phase 11.")

    def close(self) -> None:
        """Close the database connection."""
        raise NotImplementedError("Database is implemented in Phase 11.")
