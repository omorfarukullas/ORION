"""
planner/task_planner.py
=======================
Phase 12 — Multi-Step Task Planner

Decomposes multi-step commands into an ordered list of single-intent
tasks and executes them sequentially through the actions layer.
"""
from __future__ import annotations

import re
from typing import Any

from nlp.command_parser import CommandParser, ParsedCommand
from utils.logger import get_logger

logger = get_logger(__name__)


class TaskPlanner:
    """
    Breaks complex commands like *"open Chrome and search YouTube for X"*
    into an ordered list of ParsedCommand objects and executes each one.
    """

    CONJUNCTION_PATTERN = re.compile(
        r"\b(?:and\s+then|then|and|after\s+that)\b",
        flags=re.IGNORECASE,
    )

    def __init__(self, command_parser: CommandParser | None = None) -> None:
        self.parser = command_parser or CommandParser()

    def is_multi_step(self, text: str) -> bool:
        """
        Check if *text* contains multi-step task conjunctions.
        """
        if not text:
            return False
        segments = self._split_segments(text)
        if len(segments) <= 1:
            return False

        # Validate that all segments parse to a recognized intent
        for seg in segments:
            parsed = self.parser.parse(seg)
            if parsed.intent == "UNKNOWN":
                return False
        return True

    def _split_segments(self, text: str) -> list[str]:
        """Split text on task conjunctions."""
        parts = self.CONJUNCTION_PATTERN.split(text)
        cleaned = [p.strip() for p in parts if p.strip()]
        return cleaned

    def plan(self, raw_text: str) -> list[ParsedCommand]:
        """
        Decompose *raw_text* into a list of single-intent ParsedCommands.

        Args:
            raw_text: Raw transcribed spoken command.

        Returns:
            Ordered list of single-intent ParsedCommands.
        """
        segments = self._split_segments(raw_text)
        if not segments:
            segments = [raw_text]

        logger.info(f"TaskPlanner decomposed '{raw_text}' into {len(segments)} step(s): {segments}")

        commands: list[ParsedCommand] = []
        for segment in segments:
            parsed = self.parser.parse(segment)
            commands.append(parsed)

        return commands

    def execute_plan(
        self,
        steps: list[ParsedCommand],
        dispatch_fn: Any,
        confirmation_handler: Any = None,
        context: Any = None,
        db: Any = None,
    ) -> str:
        """
        Execute each step sequentially and return a combined spoken confirmation.

        Args:
            steps: List of ParsedCommands to execute in order.
            dispatch_fn: The command dispatcher function.
            confirmation_handler: Optional ConfirmationHandler instance.
            context: Optional ConversationContext instance.
            db: Optional Database instance.

        Returns:
            Combined spoken response string.
        """
        if not steps:
            return "No actions to execute."

        replies: list[str] = []

        for idx, step in enumerate(steps, start=1):
            logger.info(f"Executing plan step {idx}/{len(steps)}: {step.intent} ({step.raw_text})")

            # Resolve context if available
            resolved_step = context.resolve(step) if context else step

            # Dispatch action
            reply = dispatch_fn(
                resolved_step,
                confirmation_handler=confirmation_handler,
                db=db,
            )

            # Update context & DB if available
            if context:
                context.update(resolved_step)
            if db:
                db.log_command(
                    raw_text=resolved_step.raw_text,
                    intent=resolved_step.intent,
                    confidence=resolved_step.confidence,
                    entities=resolved_step.entities,
                    outcome=reply,
                )

            replies.append(reply)

            # If a destructive action was cancelled, halt subsequent steps
            if "Action cancelled" in reply:
                logger.warning(f"Plan halted at step {idx} due to cancellation.")
                break

        return " ".join(replies)
