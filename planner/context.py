"""
planner/context.py
==================
STUB — Phase 11

Short-term context memory: remembers last intent, entity, and
application so follow-up commands resolve correctly.
"""
from __future__ import annotations
from typing import Optional


class ConversationContext:
    """
    Tracks the most recent command's intent, entity, and open application
    to resolve ambiguous follow-up commands.

    Example (Phase 11):
        User: "Open Chrome"  → context.last_app = "chrome"
        User: "Search for Python tutorials" → resolved as YouTube/Google search
              because last_app is "chrome"

    This is in-memory only. Persistent memory lives in database/database.py.
    """

    def __init__(self) -> None:
        self.last_intent: Optional[str] = None
        self.last_entity: Optional[str] = None
        self.last_application: Optional[str] = None

    def update(self, intent: str, entity: Optional[str], application: Optional[str]) -> None:
        """Update context after a successful command execution."""
        self.last_intent = intent
        self.last_entity = entity
        self.last_application = application

    def clear(self) -> None:
        """Reset context (e.g. on wake-word timeout)."""
        self.last_intent = None
        self.last_entity = None
        self.last_application = None

    def __repr__(self) -> str:
        return (
            f"<ConversationContext intent={self.last_intent!r} "
            f"entity={self.last_entity!r} app={self.last_application!r}>"
        )
