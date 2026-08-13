"""
nlp/command_parser.py
=====================
STUB — Phase 7

Combines the intent classifier and entity extractor into a single
parsed-command object ready for the task planner.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ParsedCommand:
    """The output of the NLP pipeline — everything the planner needs."""
    raw_text: str
    intent: str
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"ParsedCommand(intent={self.intent!r}, "
            f"confidence={self.confidence:.0%}, entities={self.entities})"
        )


class CommandParser:
    """
    Orchestrates preprocessing → intent classification → entity extraction.

    Returns a :class:`ParsedCommand` for the task planner to act on.
    Phase 7 wires the full pipeline together here.
    """

    def parse(self, raw_text: str) -> ParsedCommand:
        """
        Parse *raw_text* (post wake-word stripping) into a ParsedCommand.

        Raises:
            NotImplementedError: Until Phase 7 is implemented.
        """
        raise NotImplementedError("CommandParser is implemented in Phase 7.")
