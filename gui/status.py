"""
gui/status.py
=============
STUB — Phase 10

Status bar widget: shows ORION's current state (idle / listening /
processing / speaking) and a pulsing indicator animation.
"""
from __future__ import annotations


class StatusPanel:
    """
    A CustomTkinter frame showing ORION's real-time state.

    States (Phase 10):
        IDLE       — grey dot, "Standby"
        LISTENING  — blue pulsing dot, "Listening…"
        PROCESSING — orange dot, "Processing…"
        SPEAKING   — green dot, "Speaking…"
        ERROR      — red dot, "Error"
    """

    def set_state(self, state: str) -> None:
        """Update the displayed state."""
        raise NotImplementedError("StatusPanel is implemented in Phase 10.")
