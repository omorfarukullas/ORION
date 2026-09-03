"""
tests/test_integration.py
=========================
End-to-end integration tests for ORION assistant (Phase 12).
"""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from database.database import Database
from nlp.command_dispatcher import dispatch
from nlp.command_parser import CommandParser
from planner.context import ConversationContext
from planner.task_planner import TaskPlanner


class TestIntegration:
    @pytest.fixture
    def test_env(self, tmp_path: Path):
        db = Database(tmp_path / "integration_test.db")
        context = ConversationContext()
        parser = CommandParser()
        planner = TaskPlanner(command_parser=parser)
        return {"db": db, "context": context, "parser": parser, "planner": planner}

    def test_remember_and_recall_roundtrip(self, test_env) -> None:
        db = test_env["db"]
        parser = test_env["parser"]

        # 1. User says "remember that my project folder is on Desktop"
        cmd1 = parser.parse("remember that my project folder is on Desktop")
        reply1 = dispatch(cmd1, db=db)
        assert "I will remember that my project folder is on Desktop" in reply1

        # 2. User says "what is my project folder"
        cmd2 = parser.parse("what is my project folder")
        reply2 = dispatch(cmd2, db=db)
        assert "Desktop" in reply2

    def test_destructive_intent_blocked_without_confirmation(self, test_env) -> None:
        db = test_env["db"]
        parser = test_env["parser"]

        # Handler that simulates user saying "no"
        mock_handler = MagicMock()
        mock_handler.ask.return_value = False

        cmd = parser.parse("delete file budget.xlsx")
        reply = dispatch(cmd, confirmation_handler=mock_handler, db=db)
        assert "Action cancelled" in reply
        mock_handler.ask.assert_called_once()

    def test_context_resolution_followup(self, test_env) -> None:
        test_env["db"]
        context = test_env["context"]
        parser = test_env["parser"]

        # Step 1: Open Chrome
        cmd1 = parser.parse("open chrome")
        context.update(cmd1)
        assert context.last_application == "chrome"

        # Step 2: "close it"
        cmd2 = parser.parse("close it")
        resolved2 = context.resolve(cmd2)
        assert resolved2.entities.get("app_name") == "chrome"

    def test_multi_step_planner_execution(self, test_env) -> None:
        db = test_env["db"]
        context = test_env["context"]
        planner = test_env["planner"]

        # Multi-step command: "what time is it and what is today's date"
        text = "what time is it and what is today's date"
        assert planner.is_multi_step(text) is True

        steps = planner.plan(text)
        assert len(steps) == 2

        reply = planner.execute_plan(
            steps=steps,
            dispatch_fn=dispatch,
            context=context,
            db=db,
        )
        assert "The time is" in reply
        assert "Today is" in reply
