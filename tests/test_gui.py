"""
tests/test_gui.py
=================
Unit tests for gui/ components (Phase 10).
"""
import pytest
import customtkinter as ctk
from gui.status import StatusPanel
from gui.history import HistoryPanel
from gui.metrics import MetricsBar
from gui.dashboard import Dashboard


class TestGUIComponents:
    @pytest.fixture(scope="class")
    def root(self):
        # Create a hidden dummy root window for widget testing
        app = ctk.CTk()
        app.withdraw()
        yield app
        app.destroy()

    def test_status_panel_states(self, root) -> None:
        panel = StatusPanel(root)
        assert panel.current_state == "IDLE"

        panel.set_state("LISTENING")
        assert panel.current_state == "LISTENING"
        assert panel.label.cget("text") == "Listening..."

        panel.set_state("SPEAKING")
        assert panel.current_state == "SPEAKING"
        assert panel.label.cget("text") == "Speaking..."

    def test_history_panel_add_and_clear(self, root) -> None:
        panel = HistoryPanel(root, max_entries=5)
        panel.add_entry("open chrome", "OPEN_APP", 0.95, "Opening Chrome.")
        panel.add_entry("what time is it", "TIME", 0.99, "The time is 10:00 AM.")
        assert len(panel.entries) == 2

        panel.clear()
        assert len(panel.entries) == 0

    def test_metrics_bar_instantiation(self, root) -> None:
        metrics = MetricsBar(root)
        assert "CPU:" in metrics.cpu_label.cget("text")
        assert "RAM:" in metrics.ram_label.cget("text")
        assert "Bat:" in metrics.bat_label.cget("text")
        metrics.stop()

    def test_dashboard_instantiation(self) -> None:
        dash = Dashboard()
        dash.withdraw()
        dash.update_status("PROCESSING")
        dash.update_command(
            raw_text="search google for AI",
            intent="WEB_SEARCH",
            confidence=0.91,
            entities={"query": "AI"},
            outcome="Searching Google for AI.",
        )
        dash.metrics_bar.stop()
        dash.destroy()
