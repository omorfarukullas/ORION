"""
gui/metrics.py
==============
Phase 10 — System Metrics Bar

Displays live CPU %, RAM usage, and battery status with auto-refresh.
"""
from __future__ import annotations

import customtkinter as ctk
import psutil


class MetricsBar(ctk.CTkFrame):
    """
    Component displaying real-time system metrics (CPU, RAM, Battery).
    """

    def __init__(self, master: ctk.CTkBaseClass, refresh_ms: int = 2000, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.refresh_ms = refresh_ms
        self._running = True

        self.cpu_label = ctk.CTkLabel(
            self,
            text="CPU: --%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3a86ff",
        )
        self.cpu_label.pack(side="left", expand=True, padx=5, pady=6)

        self.ram_label = ctk.CTkLabel(
            self,
            text="RAM: -- / -- GB",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8338ec",
        )
        self.ram_label.pack(side="left", expand=True, padx=5, pady=6)

        self.bat_label = ctk.CTkLabel(
            self,
            text="Battery: --%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#06d6a0",
        )
        self.bat_label.pack(side="left", expand=True, padx=5, pady=6)

        # Prime baseline measurement for CPU
        try:
            psutil.cpu_percent(interval=None)
        except Exception:
            pass

        self.refresh_metrics()

    def refresh_metrics(self) -> None:
        """Fetch current hardware stats and update labels."""
        if not self._running:
            return

        try:
            # CPU
            cpu = psutil.cpu_percent(interval=None)
            self.cpu_label.configure(text=f"CPU: {cpu:.0f}%")

            # RAM
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
            self.ram_label.configure(text=f"RAM: {used_gb:.1f}/{total_gb:.1f} GB")

            # Battery
            bat = psutil.sensors_battery()
            if bat is not None:
                plugged = " ⚡" if bat.power_plugged else ""
                self.bat_label.configure(text=f"Bat: {int(bat.percent)}%{plugged}")
            else:
                self.bat_label.configure(text="Bat: N/A")
        except Exception:
            pass

        # Schedule next update
        try:
            self.after(self.refresh_ms, self.refresh_metrics)
        except Exception:
            pass

    def stop(self) -> None:
        """Stop refresh timer."""
        self._running = False
