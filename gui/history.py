"""
gui/history.py
==============
Phase 10 — Command History Panel

Scrollable command history panel showing recent commands with their
intent, entity, confidence score, and outcome.
"""
from __future__ import annotations

from datetime import datetime

import customtkinter as ctk


class HistoryPanel(ctk.CTkScrollableFrame):
    """
    A CustomTkinter scrollable frame listing recent ORION commands.
    """

    def __init__(self, master: ctk.CTkBaseClass, max_entries: int = 20, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.max_entries = max_entries
        self.entries: list[ctk.CTkFrame] = []

    def add_entry(
        self,
        raw_text: str,
        intent: str,
        confidence: float,
        outcome: str,
    ) -> None:
        """
        Prepend a new command entry to the history list.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Row container
        row = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=6)
        row.pack(fill="x", padx=4, pady=3)

        # Header line: [time] intent (confidence)
        conf_pct = f"{confidence:.0%}" if confidence is not None else "--%"

        # Color coding by outcome / confidence
        if "cancel" in outcome.lower() or "abort" in outcome.lower():
            badge_color = "#e63946"
        elif confidence < 0.8:
            badge_color = "#f4a261"
        else:
            badge_color = "#2a9d8f"

        top_line = ctk.CTkFrame(row, fg_color="transparent")
        top_line.pack(fill="x", padx=6, pady=(4, 2))

        time_lbl = ctk.CTkLabel(
            top_line,
            text=timestamp,
            font=ctk.CTkFont(size=11),
            text_color="gray60",
        )
        time_lbl.pack(side="left")

        intent_badge = ctk.CTkLabel(
            top_line,
            text=f" {intent} ({conf_pct}) ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=badge_color,
            text_color="white",
            corner_radius=4,
        )
        intent_badge.pack(side="left", padx=8)

        # Command text
        cmd_lbl = ctk.CTkLabel(
            row,
            text=f"🗣 \"{raw_text}\"",
            font=ctk.CTkFont(size=12, slant="italic"),
            anchor="w",
        )
        cmd_lbl.pack(fill="x", padx=8, pady=(0, 2))

        # Outcome summary
        out_lbl = ctk.CTkLabel(
            row,
            text=f"🤖 {outcome}",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray70"),
            anchor="w",
        )
        out_lbl.pack(fill="x", padx=8, pady=(0, 4))

        self.entries.insert(0, row)

        # Trim old entries
        while len(self.entries) > self.max_entries:
            oldest = self.entries.pop()
            oldest.destroy()

    def clear(self) -> None:
        """Remove all history entries from the panel."""
        for entry in self.entries:
            entry.destroy()
        self.entries.clear()
