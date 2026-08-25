"""
tests/test_database.py
======================
Unit tests for database/database.py (Phase 11).
"""
from pathlib import Path
import pytest
from database.database import Database


class TestDatabase:
    @pytest.fixture
    def db(self, tmp_path: Path) -> Database:
        db_file = tmp_path / "test_orion.db"
        return Database(db_file)

    def test_log_and_get_command_history(self, db: Database) -> None:
        db.log_command(
            raw_text="open chrome",
            intent="OPEN_APP",
            confidence=0.95,
            entities={"app_name": "chrome"},
            outcome="Opening Chrome.",
        )

        history = db.get_recent_commands(limit=5)
        assert len(history) == 1
        entry = history[0]
        assert entry["raw_text"] == "open chrome"
        assert entry["intent"] == "OPEN_APP"
        assert entry["confidence"] == 0.95
        assert "Opening Chrome." in entry["outcome"]

    def test_save_and_recall_memory(self, db: Database) -> None:
        db.save_memory("project_folder", "Desktop/AI_Projects")
        val = db.recall_memory("project_folder")
        assert val == "Desktop/AI_Projects"

        # Update memory
        db.save_memory("project_folder", "Desktop/New_AI")
        assert db.recall_memory("project_folder") == "Desktop/New_AI"

    def test_fuzzy_recall_memory(self, db: Database) -> None:
        db.save_memory("my project folder", "Desktop/Orion")
        val = db.recall_memory("project folder")
        assert val == "Desktop/Orion"

    def test_list_and_delete_memories(self, db: Database) -> None:
        db.save_memory("key1", "val1")
        db.save_memory("key2", "val2")

        memories = db.list_memories()
        assert len(memories) == 2
        assert memories["key1"] == "val1"

        deleted = db.delete_memory("key1")
        assert deleted is True
        assert db.recall_memory("key1") is None
        assert len(db.list_memories()) == 1
