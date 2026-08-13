"""
gui/history.py
==============
STUB — Phase 10

Scrollable command history panel showing recent commands with their
intent, entity, confidence score, and outcome.
"""
from __future__ import annotations


class HistoryPanel:
    """
    A CustomTkinter scrollable frame listing recent ORION commands.

    Each row shows (Phase 10):
        timestamp | raw text | intent | confidence | outcome
    """

    def add_entry(
        self,
        raw_text: str,
        intent: str,
        confidence: float,
        outcome: str,
    ) -> None:
        """Prepend a new command entry to the history list."""
        raise NotImplementedError("HistoryPanel is implemented in Phase 10.")

    def clear(self) -> None:
        """Remove all history entries from the panel."""
        raise NotImplementedError("HistoryPanel is implemented in Phase 10.")
