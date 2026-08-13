"""
gui/dashboard.py
================
STUB — Phase 10

Main CustomTkinter dashboard window. Shows online status, listening
indicator, last command details, and live system stats.
"""
from __future__ import annotations


class Dashboard:
    """
    Root CustomTkinter window for ORION.

    Layout (Phase 10):
        ┌──────────────────────────────────┐
        │  ORION        ● Online           │
        │  [Listening indicator]           │
        ├──────────────────────────────────┤
        │  Last Command                    │
        │  Intent / Entity / Confidence    │
        ├──────────────────────────────────┤
        │  CPU: 34%  RAM: 6.2 GB  Bat: 72%│
        ├──────────────────────────────────┤
        │  Recent History                  │
        │  [CommandHistoryPanel]           │
        └──────────────────────────────────┘
    """

    def __init__(self) -> None:
        raise NotImplementedError("Dashboard is implemented in Phase 10.")

    def run(self) -> None:
        """Start the Tkinter main loop."""
        raise NotImplementedError("Dashboard is implemented in Phase 10.")

    def update_status(self, state: str) -> None:
        """Update the listening/processing status indicator."""
        raise NotImplementedError("Dashboard is implemented in Phase 10.")
