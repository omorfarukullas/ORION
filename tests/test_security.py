"""
tests/test_security.py
======================
Security module unit tests (Phase 9).
"""
import json
from pathlib import Path
from unittest.mock import MagicMock
import numpy as np

import pytest
from security.command_validator import get_risk_level, is_safe, is_destructive, RiskLevel
from security.permissions import can_write, audit_log
from security.confirmation import ConfirmationHandler
from nlp.command_dispatcher import dispatch


class TestCommandValidator:
    """Tests for intent risk classification and validator functions."""

    def test_open_app_is_safe(self) -> None:
        assert get_risk_level("OPEN_APP") == RiskLevel.SAFE
        assert is_safe("OPEN_APP") is True
        assert is_destructive("OPEN_APP") is False

    def test_delete_file_is_destructive(self) -> None:
        assert get_risk_level("DELETE_FILE") == RiskLevel.DESTRUCTIVE
        assert is_destructive("DELETE_FILE") is True
        assert is_safe("DELETE_FILE") is False

    def test_unknown_intent_is_forbidden(self) -> None:
        assert get_risk_level("RUN_SHELL_COMMAND") == RiskLevel.FORBIDDEN
        assert is_safe("RUN_SHELL_COMMAND") is False
        assert is_destructive("RUN_SHELL_COMMAND") is False

    def test_screenshot_is_safe(self) -> None:
        assert get_risk_level("SCREENSHOT") == RiskLevel.SAFE
        assert is_safe("SCREENSHOT") is True

    def test_shutdown_is_destructive(self) -> None:
        assert get_risk_level("SHUTDOWN") == RiskLevel.DESTRUCTIVE
        assert is_destructive("SHUTDOWN") is True


class TestPermissions:
    """Tests for write permissions and audit logging."""

    def test_can_write_allowed(self) -> None:
        desktop_file = Path.home() / "Desktop" / "test.txt"
        assert can_write(desktop_file) is True

    def test_can_write_disallowed(self) -> None:
        sys_file = Path("C:/Windows/System32/drivers/etc/hosts")
        assert can_write(sys_file) is False

    def test_audit_log(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr("config.settings.Settings.LOGS_DIR", tmp_path)
        audit_log("DELETE_FILE", "test.txt", "EXECUTED_SUCCESS")

        log_file = tmp_path / "audit.jsonl"
        assert log_file.exists()

        content = log_file.read_text(encoding="utf-8").strip()
        data = json.loads(content)
        assert data["intent"] == "DELETE_FILE"
        assert data["entity"] == "test.txt"
        assert data["outcome"] == "EXECUTED_SUCCESS"


class TestConfirmationHandler:
    """Tests for ConfirmationHandler user verification loop."""

    def test_confirmation_yes(self) -> None:
        mock_tts = MagicMock()
        mock_listener = MagicMock()
        mock_listener.record.return_value = np.zeros(100, dtype=np.float32)
        mock_stt = MagicMock()
        mock_stt.transcribe.return_value = "yes"

        handler = ConfirmationHandler(tts=mock_tts, listener=mock_listener, stt=mock_stt)
        assert handler.ask("delete test.txt") is True
        mock_tts.speak.assert_called_once()
        mock_listener.record.assert_called_once()

    def test_confirmation_no(self) -> None:
        mock_tts = MagicMock()
        mock_listener = MagicMock()
        mock_listener.record.return_value = np.zeros(100, dtype=np.float32)
        mock_stt = MagicMock()
        mock_stt.transcribe.return_value = "no do not do that"

        handler = ConfirmationHandler(tts=mock_tts, listener=mock_listener, stt=mock_stt)
        assert handler.ask("delete test.txt") is False

    def test_dispatcher_destructive_gated(self) -> None:
        class DummyCmd:
            intent = "DELETE_FILE"
            confidence = 1.0
            entities = {"file_name": "important.txt"}
            raw_text = "delete file important.txt"

        mock_handler = MagicMock()
        mock_handler.ask.return_value = False

        res = dispatch(DummyCmd(), confirmation_handler=mock_handler)
        assert "Action cancelled" in res
        mock_handler.ask.assert_called_once()
