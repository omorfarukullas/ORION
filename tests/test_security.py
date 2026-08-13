"""
tests/test_security.py
======================
Security module tests — populated in Phase 9.
"""
import pytest
from security.command_validator import get_risk_level, RiskLevel


class TestCommandValidator:
    """Tests for the intent risk classification table."""

    def test_open_app_is_safe(self) -> None:
        assert get_risk_level("OPEN_APP") == RiskLevel.SAFE

    def test_delete_file_is_destructive(self) -> None:
        assert get_risk_level("DELETE_FILE") == RiskLevel.DESTRUCTIVE

    def test_unknown_intent_is_forbidden(self) -> None:
        assert get_risk_level("RUN_SHELL_COMMAND") == RiskLevel.FORBIDDEN

    def test_screenshot_is_safe(self) -> None:
        assert get_risk_level("SCREENSHOT") == RiskLevel.SAFE

    def test_shutdown_is_destructive(self) -> None:
        assert get_risk_level("SHUTDOWN") == RiskLevel.DESTRUCTIVE
