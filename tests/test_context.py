"""
tests/test_context.py
=====================
Unit tests for planner/context.py (Phase 11).
"""
import pytest
from nlp.command_parser import ParsedCommand
from planner.context import ConversationContext


class TestConversationContext:
    @pytest.fixture
    def context(self) -> ConversationContext:
        return ConversationContext()

    def test_update_and_resolve_app(self, context: ConversationContext) -> None:
        cmd1 = ParsedCommand(
            raw_text="open chrome",
            intent="OPEN_APP",
            confidence=0.95,
            entities={"app_name": "chrome"},
        )
        context.update(cmd1)
        assert context.last_application == "chrome"

        cmd2 = ParsedCommand(
            raw_text="close it",
            intent="CLOSE_APP",
            confidence=0.85,
            entities={"app_name": "it"},
        )
        resolved = context.resolve(cmd2)
        assert resolved.entities.get("app_name") == "chrome"

    def test_resolve_search_query(self, context: ConversationContext) -> None:
        cmd1 = ParsedCommand(
            raw_text="search for python tutorials",
            intent="WEB_SEARCH",
            confidence=0.92,
            entities={"query": "python tutorials"},
        )
        context.update(cmd1)

        cmd2 = ParsedCommand(
            raw_text="search youtube for it",
            intent="YOUTUBE_SEARCH",
            confidence=0.90,
            entities={"query": "it"},
        )
        resolved = context.resolve(cmd2)
        assert resolved.entities.get("query") == "python tutorials"

    def test_clear_context(self, context: ConversationContext) -> None:
        cmd = ParsedCommand(
            raw_text="open chrome",
            intent="OPEN_APP",
            confidence=0.95,
            entities={"app_name": "chrome"},
        )
        context.update(cmd)
        context.clear()
        assert context.last_application is None
        assert context.last_intent is None
