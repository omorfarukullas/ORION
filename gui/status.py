"""
gui/status.py
=============
Phase 10 — Status Panel Widget

Status bar widget: shows ORION's current state (idle / listening /
processing / speaking / error) with color-coded indicator and pulsing effect.
"""
from __future__ import annotations

import customtkinter as ctk


class StatusPanel(ctk.CTkFrame):
    """
    A CustomTkinter frame showing ORION's real-time state.

    States:
        IDLE       — grey dot, "Standby"
        LISTENING  — cyan/blue dot, "Listening…"
        PROCESSING — orange dot, "Processing…"
        SPEAKING   — green dot, "Speaking…"
        ERROR      — red dot, "Error"
    """

    STATE_CONFIG = {
        "IDLE": {"color": "#808080", "label": "Standby"},
        "LISTENING": {"color": "#1f6aa5", "label": "Listening..."},
        "PROCESSING": {"color": "#e59400", "label": "Processing..."},
        "SPEAKING": {"color": "#2fa572", "label": "Speaking..."},
        "ERROR": {"color": "#d32f2f", "label": "Error"},
    }

    def __init__(self, master: ctk.CTkBaseClass, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.current_state = "IDLE"
        self._pulse_state = False

        # Status indicator dot
        self.dot = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.STATE_CONFIG["IDLE"]["color"],
        )
        self.dot.pack(side="left", padx=(10, 5), pady=5)

        # Status text label
        self.label = ctk.CTkLabel(
            self,
            text=self.STATE_CONFIG["IDLE"]["label"],
            font=ctk.CTkFont(size=14, weight="normal"),
        )
        self.label.pack(side="left", padx=(0, 10), pady=5)

    def set_state(self, state: str) -> None:
        """
        Update the displayed state.

        Args:
            state: One of IDLE, LISTENING, PROCESSING, SPEAKING, ERROR
        """
        normalized_state = state.upper().strip()
        config = self.STATE_CONFIG.get(normalized_state, self.STATE_CONFIG["IDLE"])
        self.current_state = normalized_state

        self.dot.configure(text_color=config["color"])
        self.label.configure(text=config["label"])
