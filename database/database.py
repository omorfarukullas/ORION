"""
database/database.py
====================
Phase 11 — SQLite Database Layer

SQLite persistence layer for ORION's long-term memory and command history.
"""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class Database:
    """
    SQLite wrapper for ORION's persistent storage.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self.connect()

    def connect(self) -> None:
        """Open (or create) the SQLite database and create tables."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._create_tables()
            logger.info(f"Database connected at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database at {self.db_path}: {e}")

    def _create_tables(self) -> None:
        """Initialize database schema."""
        if not self._conn:
            return

        with self._conn:
            # Command History Table
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    raw_text TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    confidence REAL,
                    entities_json TEXT,
                    outcome TEXT
                )
            """)

            # Persistent Memories (Key-Value) Table
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Key-Value User Preferences Table
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

    def log_command(
        self,
        raw_text: str,
        intent: str,
        confidence: float = 1.0,
        entities: Dict[str, Any] | None = None,
        outcome: str = "",
    ) -> None:
        """Persist a command and its outcome to command_history."""
        if not self._conn:
            return

        try:
            now = datetime.now().isoformat()
            ent_json = json.dumps(entities or {})
            with self._conn:
                self._conn.execute(
                    """
                    INSERT INTO command_history (timestamp, raw_text, intent, confidence, entities_json, outcome)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (now, raw_text, intent, confidence, ent_json, outcome),
                )
        except Exception as e:
            logger.error(f"Failed to log command to database: {e}")

    def get_recent_commands(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch recent command history entries."""
        if not self._conn:
            return []

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "SELECT * FROM command_history ORDER BY id DESC LIMIT ?", (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch recent commands: {e}")
            return []

    def save_memory(self, key: str, value: str) -> None:
        """Store or update a user-defined memory."""
        if not self._conn or not key:
            return

        try:
            now = datetime.now().isoformat()
            clean_key = key.lower().strip()
            with self._conn:
                self._conn.execute(
                    """
                    INSERT INTO memories (key, value, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = excluded.updated_at
                    """,
                    (clean_key, value.strip(), now, now),
                )
            logger.info(f"Memory saved: '{clean_key}' -> '{value}'")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def remember(self, key: str, value: str) -> None:
        """Alias for save_memory."""
        self.save_memory(key, value)

    def recall_memory(self, key: str) -> Optional[str]:
        """Retrieve a stored memory value by key, or None if not found."""
        if not self._conn or not key:
            return None

        try:
            clean_key = key.lower().strip()
            cursor = self._conn.cursor()
            cursor.execute("SELECT value FROM memories WHERE key = ?", (clean_key,))
            row = cursor.fetchone()
            if row:
                return row["value"]
            
            # Fuzzy match / contains fallback
            cursor.execute("SELECT value FROM memories WHERE key LIKE ? OR ? LIKE ('%' || key || '%')", (f"%{clean_key}%", clean_key))
            fuzzy_row = cursor.fetchone()
            if fuzzy_row:
                return fuzzy_row["value"]

            return None
        except Exception as e:
            logger.error(f"Failed to recall memory '{key}': {e}")
            return None

    def recall(self, key: str) -> Optional[str]:
        """Alias for recall_memory."""
        return self.recall_memory(key)

    def list_memories(self) -> Dict[str, str]:
        """List all saved memories as a dictionary."""
        if not self._conn:
            return {}

        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT key, value FROM memories ORDER BY key ASC")
            rows = cursor.fetchall()
            return {row["key"]: row["value"] for row in rows}
        except Exception as e:
            logger.error(f"Failed to list memories: {e}")
            return {}

    def delete_memory(self, key: str) -> bool:
        """Delete a stored memory by key."""
        if not self._conn or not key:
            return False

        try:
            clean_key = key.lower().strip()
            with self._conn:
                cursor = self._conn.execute("DELETE FROM memories WHERE key = ?", (clean_key,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete memory '{key}': {e}")
            return False

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            try:
                self._conn.close()
                self._conn = None
                logger.info("Database connection closed.")
            except Exception as e:
                logger.error(f"Error closing database: {e}")
