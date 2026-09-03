"""
gui/settings_panel.py
=====================
Phase C — Settings Control Panel

CustomTkinter frame providing live UI controls to adjust ORION's settings
(confidence thresholds, TTS speech rate, Ollama LLM toggle, theme).
"""
from __future__ import annotations
import customtkinter as ctk
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class SettingsPanel(ctk.CTkFrame):
    """
    Control panel for tuning ORION thresholds and runtime preferences.
    """

    def __init__(self, master: ctk.CTkBaseClass, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.title_lbl = ctk.CTkLabel(
            self,
            text="⚙ System Settings & Calibration",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.title_lbl.pack(anchor="w", padx=16, pady=(12, 8))

        # ── 1. Confidence Threshold Sliders ───────────────────────────
        self.thresh_frame = ctk.CTkFrame(self, corner_radius=8)
        self.thresh_frame.pack(fill="x", padx=12, pady=6)

        # Execute Threshold
        self.exec_label = ctk.CTkLabel(
            self.thresh_frame,
            text=f"Execute Confidence Threshold: {Settings.CONFIDENCE_EXECUTE:.0%}",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.exec_label.pack(anchor="w", padx=12, pady=(8, 2))

        self.exec_slider = ctk.CTkSlider(
            self.thresh_frame,
            from_=0.40,
            to=0.95,
            number_of_steps=55,
            command=self._on_exec_slider,
        )
        self.exec_slider.set(Settings.CONFIDENCE_EXECUTE)
        self.exec_slider.pack(fill="x", padx=12, pady=(0, 8))

        # Confirm Threshold
        self.confirm_label = ctk.CTkLabel(
            self.thresh_frame,
            text=f"Confirm Confidence Threshold: {Settings.CONFIDENCE_CONFIRM:.0%}",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.confirm_label.pack(anchor="w", padx=12, pady=(4, 2))

        self.confirm_slider = ctk.CTkSlider(
            self.thresh_frame,
            from_=0.20,
            to=0.65,
            number_of_steps=45,
            command=self._on_confirm_slider,
        )
        self.confirm_slider.set(Settings.CONFIDENCE_CONFIRM)
        self.confirm_slider.pack(fill="x", padx=12, pady=(0, 10))

        # ── 2. Ollama LLM Toggle ──────────────────────────────────────
        self.llm_frame = ctk.CTkFrame(self, corner_radius=8)
        self.llm_frame.pack(fill="x", padx=12, pady=6)

        self.llm_switch = ctk.CTkSwitch(
            self.llm_frame,
            text="Enable Local Ollama AI (Ask Orion)",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_llm_toggle,
        )
        if Settings.OLLAMA_ENABLED:
            self.llm_switch.select()
        else:
            self.llm_switch.deselect()
        self.llm_switch.pack(anchor="w", padx=12, pady=10)

        # ── 3. TTS Speech Rate Slider ─────────────────────────────────
        self.tts_frame = ctk.CTkFrame(self, corner_radius=8)
        self.tts_frame.pack(fill="x", padx=12, pady=6)

        self.tts_label = ctk.CTkLabel(
            self.tts_frame,
            text=f"TTS Speech Rate: {Settings.TTS_RATE} WPM",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.tts_label.pack(anchor="w", padx=12, pady=(8, 2))

        self.tts_slider = ctk.CTkSlider(
            self.tts_frame,
            from_=120,
            to=260,
            number_of_steps=28,
            command=self._on_tts_slider,
        )
        self.tts_slider.set(Settings.TTS_RATE)
        self.tts_slider.pack(fill="x", padx=12, pady=(0, 10))

        # ── 4. Voice Persona Dropdown ─────────────────────────────────
        from speech.personas import persona_manager

        self.persona_frame = ctk.CTkFrame(self, corner_radius=8)
        self.persona_frame.pack(fill="x", padx=12, pady=6)

        self.persona_lbl = ctk.CTkLabel(
            self.persona_frame,
            text="Voice Persona & Style:",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.persona_lbl.pack(side="left", padx=12, pady=10)

        self.persona_option = ctk.CTkOptionMenu(
            self.persona_frame,
            values=["Professional ORION", "Friendly Mode", "Coqui TTS / Custom Voice"],
            command=self._on_persona_select,
        )
        self.persona_option.set(persona_manager.active_persona.name)
        self.persona_option.pack(side="right", padx=12, pady=10)

        # ── 5. GUI Theme Dropdown ─────────────────────────────────────
        self.theme_frame = ctk.CTkFrame(self, corner_radius=8)
        self.theme_frame.pack(fill="x", padx=12, pady=6)

        self.theme_lbl = ctk.CTkLabel(
            self.theme_frame,
            text="GUI Appearance Mode:",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.theme_lbl.pack(side="left", padx=12, pady=10)

        self.theme_option = ctk.CTkOptionMenu(
            self.theme_frame,
            values=["dark", "light", "system"],
            command=self._on_theme_select,
        )
        self.theme_option.set(Settings.GUI_THEME)
        self.theme_option.pack(side="right", padx=12, pady=10)

    def _on_exec_slider(self, val: float) -> None:
        Settings.CONFIDENCE_EXECUTE = round(val, 2)
        self.exec_label.configure(text=f"Execute Confidence Threshold: {Settings.CONFIDENCE_EXECUTE:.0%}")
        Settings.save_user_settings()
        logger.info(f"Updated Settings.CONFIDENCE_EXECUTE -> {Settings.CONFIDENCE_EXECUTE}")

    def _on_confirm_slider(self, val: float) -> None:
        Settings.CONFIDENCE_CONFIRM = round(val, 2)
        self.confirm_label.configure(text=f"Confirm Confidence Threshold: {Settings.CONFIDENCE_CONFIRM:.0%}")
        Settings.save_user_settings()
        logger.info(f"Updated Settings.CONFIDENCE_CONFIRM -> {Settings.CONFIDENCE_CONFIRM}")

    def _on_llm_toggle(self) -> None:
        Settings.OLLAMA_ENABLED = bool(self.llm_switch.get())
        Settings.save_user_settings()
        logger.info(f"Updated Settings.OLLAMA_ENABLED -> {Settings.OLLAMA_ENABLED}")

    def _on_tts_slider(self, val: float) -> None:
        Settings.TTS_RATE = int(val)
        self.tts_label.configure(text=f"TTS Speech Rate: {Settings.TTS_RATE} WPM")
        Settings.save_user_settings()
        logger.info(f"Updated Settings.TTS_RATE -> {Settings.TTS_RATE}")

    def _on_persona_select(self, choice: str) -> None:
        from speech.personas import persona_manager
        persona_manager.set_persona(choice)
        Settings.VOICE_PERSONA = persona_manager.active_persona.id
        Settings.save_user_settings()
        logger.info(f"GUI updated active voice persona -> {choice}")

    def _on_theme_select(self, choice: str) -> None:
        Settings.GUI_THEME = choice
        ctk.set_appearance_mode(choice)
        Settings.save_user_settings()
        logger.info(f"Updated GUI Appearance Mode -> {choice}")
