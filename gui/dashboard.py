"""
gui/dashboard.py
================
Phase 10 — Main Dashboard Window

CustomTkinter dashboard window. Shows online status, listening
indicator, last command details, live system stats, and command history.
"""
from __future__ import annotations
import threading
from typing import Any, Dict
import customtkinter as ctk

from config.settings import Settings
from gui.status import StatusPanel
from gui.metrics import MetricsBar
from gui.history import HistoryPanel


class Dashboard(ctk.CTk):
    """
    Root CustomTkinter window for ORION.
    """

    def __init__(self) -> None:
        super().__init__()

        # Appearance configuration
        ctk.set_appearance_mode(Settings.GUI_THEME)
        ctk.set_default_color_theme(Settings.GUI_COLOR_THEME)

        self.title(f"{Settings.NAME} — AI Voice Assistant (v{Settings.VERSION})")
        self.geometry("540x680")
        self.minsize(480, 560)

        # ── Top Bar / Header ───────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=16, pady=(14, 8))

        self.app_title = ctk.CTkLabel(
            self.header_frame,
            text="⚡ ORION",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.app_title.pack(side="left")

        self.status_panel = StatusPanel(self.header_frame, fg_color=("gray85", "gray20"), corner_radius=12)
        self.status_panel.pack(side="right")

        # ── Last Command Card ──────────────────────────────────────────────
        self.cmd_card = ctk.CTkFrame(self, corner_radius=10)
        self.cmd_card.pack(fill="x", padx=16, pady=8)

        self.cmd_card_title = ctk.CTkLabel(
            self.cmd_card,
            text="LAST COMMAND",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray60",
        )
        self.cmd_card_title.pack(anchor="w", padx=14, pady=(10, 2))

        self.last_text_lbl = ctk.CTkLabel(
            self.cmd_card,
            text="\"Awaiting wake word...\"",
            font=ctk.CTkFont(size=14, slant="italic"),
            anchor="w",
        )
        self.last_text_lbl.pack(fill="x", padx=14, pady=2)

        self.cmd_meta_frame = ctk.CTkFrame(self.cmd_card, fg_color="transparent")
        self.cmd_meta_frame.pack(fill="x", padx=14, pady=(4, 10))

        self.intent_lbl = ctk.CTkLabel(
            self.cmd_meta_frame,
            text="Intent: --",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3a86ff",
        )
        self.intent_lbl.pack(side="left", padx=(0, 10))

        self.conf_lbl = ctk.CTkLabel(
            self.cmd_meta_frame,
            text="Confidence: --",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
        )
        self.conf_lbl.pack(side="left", padx=(0, 10))

        self.entities_lbl = ctk.CTkLabel(
            self.cmd_meta_frame,
            text="Entities: --",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
        )
        self.entities_lbl.pack(side="left")

        # ── System Metrics Bar ─────────────────────────────────────────────
        self.metrics_bar = MetricsBar(self, fg_color=("gray85", "gray20"), corner_radius=8)
        self.metrics_bar.pack(fill="x", padx=16, pady=6)

        # ── History Section Header ─────────────────────────────────────────
        self.hist_header = ctk.CTkFrame(self, fg_color="transparent")
        self.hist_header.pack(fill="x", padx=16, pady=(10, 4))

        self.hist_title = ctk.CTkLabel(
            self.hist_header,
            text="📜 Command History",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.hist_title.pack(side="left")

        self.clear_btn = ctk.CTkButton(
            self.hist_header,
            text="Clear",
            width=55,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="gray40",
            hover_color="gray30",
            command=self._on_clear_history,
        )
        self.clear_btn.pack(side="right")

        # ── History Scrollable Panel ───────────────────────────────────────
        self.history_panel = HistoryPanel(self, corner_radius=10)
        self.history_panel.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def _on_clear_history(self) -> None:
        self.history_panel.clear()

    # ── Thread-Safe Public Update Methods ──────────────────────────────────

    def update_status(self, state: str) -> None:
        """
        Thread-safe update of the assistant status indicator.
        """
        try:
            self.after(0, lambda: self.status_panel.set_state(state))
        except Exception:
            pass

    def update_command(
        self,
        raw_text: str,
        intent: str,
        confidence: float,
        entities: Dict[str, Any] | None = None,
        outcome: str = "",
    ) -> None:
        """
        Thread-safe update of the Last Command card and History list.
        """
        entities_dict = entities or {}

        def _apply():
            # Update Last Command Card
            self.last_text_lbl.configure(text=f"\"{raw_text}\"")
            self.intent_lbl.configure(text=f"Intent: {intent}")
            self.conf_lbl.configure(text=f"Confidence: {confidence:.0%}")
            
            ent_str = ", ".join(f"{k}={v}" for k, v in entities_dict.items()) if entities_dict else "None"
            self.entities_lbl.configure(text=f"Entities: {ent_str}")

            # Append to History Panel
            self.history_panel.add_entry(
                raw_text=raw_text,
                intent=intent,
                confidence=confidence,
                outcome=outcome,
            )

        try:
            self.after(0, _apply)
        except Exception:
            pass

    def run(self) -> None:
        """Start the Tkinter GUI mainloop (blocking)."""
        self.mainloop()


def launch_dashboard() -> Dashboard:
    """Helper to instantiate Dashboard."""
    return Dashboard()
