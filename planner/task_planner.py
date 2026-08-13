"""
planner/task_planner.py
=======================
STUB — Phase 11

Decomposes multi-step commands into an ordered list of single-intent
tasks and executes them sequentially through the actions layer.
"""
from __future__ import annotations
from typing import List
from nlp.command_parser import ParsedCommand


class TaskPlanner:
    """
    Breaks complex commands like *"open Chrome and search YouTube for X"*
    into an ordered list of :class:`~nlp.command_parser.ParsedCommand`
    objects and executes each one, feeding results forward.

    Phase 11 will use simple conjunction splitting ("and", "then") to
    detect multi-step commands before handing them to the NLP pipeline.
    """

    def plan(self, command: ParsedCommand) -> List[ParsedCommand]:
        """
        Decompose *command* into a list of single-intent steps.

        Args:
            command: The output of CommandParser.parse().

        Returns:
            Ordered list of single-intent ParsedCommands.

        Raises:
            NotImplementedError: Until Phase 11 is implemented.
        """
        raise NotImplementedError("TaskPlanner is implemented in Phase 11.")

    def execute_plan(self, steps: List[ParsedCommand]) -> str:
        """
        Execute each step and return a combined spoken confirmation.

        Raises:
            NotImplementedError: Until Phase 11 is implemented.
        """
        raise NotImplementedError("TaskPlanner is implemented in Phase 11.")
