"""
tests/test_planner.py
=====================
Unit tests for planner/task_planner.py (Phase 12).
"""
from unittest.mock import MagicMock

import pytest

from nlp.command_parser import ParsedCommand
from planner.task_planner import TaskPlanner


class TestTaskPlanner:
    @pytest.fixture
    def planner(self) -> TaskPlanner:
        return TaskPlanner()

    def test_single_step_passthrough(self, planner: TaskPlanner) -> None:
        text = "open chrome"
        assert planner.is_multi_step(text) is False
        steps = planner.plan(text)
        assert len(steps) == 1
        assert steps[0].intent == "OPEN_APP"

    def test_conjunction_and_split(self, planner: TaskPlanner) -> None:
        text = "open chrome and take a screenshot"
        assert planner.is_multi_step(text) is True
        steps = planner.plan(text)
        assert len(steps) == 2
        assert steps[0].intent == "OPEN_APP"
        assert steps[1].intent == "SCREENSHOT"

    def test_conjunction_then_split(self, planner: TaskPlanner) -> None:
        text = "search google for python then open notepad"
        assert planner.is_multi_step(text) is True
        steps = planner.plan(text)
        assert len(steps) == 2
        assert steps[0].intent == "WEB_SEARCH"
        assert steps[1].intent == "OPEN_APP"

    def test_execute_plan_sequential(self, planner: TaskPlanner) -> None:
        mock_dispatcher = MagicMock()
        mock_dispatcher.side_effect = ["Opening Chrome.", "Screenshot saved."]

        step1 = ParsedCommand("open chrome", "OPEN_APP", 0.95, {"app_name": "chrome"})
        step2 = ParsedCommand("take a screenshot", "SCREENSHOT", 0.95, {})

        result = planner.execute_plan([step1, step2], dispatch_fn=mock_dispatcher)
        assert "Opening Chrome. Screenshot saved." in result
        assert mock_dispatcher.call_count == 2

    def test_execute_plan_halt_on_cancel(self, planner: TaskPlanner) -> None:
        mock_dispatcher = MagicMock()
        mock_dispatcher.side_effect = ["Action cancelled.", "Should not run"]

        step1 = ParsedCommand("delete file test.txt", "DELETE_FILE", 0.95, {"file_name": "test.txt"})
        step2 = ParsedCommand("open chrome", "OPEN_APP", 0.95, {"app_name": "chrome"})

        result = planner.execute_plan([step1, step2], dispatch_fn=mock_dispatcher)
        assert result == "Action cancelled."
        assert mock_dispatcher.call_count == 1
