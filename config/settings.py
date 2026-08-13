"""
config/settings.py
==================
Central configuration for ORION.

All tuneable knobs live here so that no magic numbers are scattered
across the codebase. Import with:

    from config.settings import Settings
    s = Settings()
"""

import os
import platform
from pathlib import Path


class Settings:
    """Singleton-style config object. Instantiate once in app.py."""

    # ── Project metadata ───────────────────────────────────────────────────────
    VERSION: str = "0.1.0"
    NAME: str = "ORION"

    # ── Platform detection ─────────────────────────────────────────────────────
    PLATFORM: str = platform.system()  # "Windows" | "Darwin" | "Linux"

    # ── Paths ──────────────────────────────────────────────────────────────────
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    CONFIG_DIR: Path = ROOT_DIR / "config"
    DATA_DIR: Path = ROOT_DIR / "data"
    MODELS_DIR: Path = ROOT_DIR / "models"
    LOGS_DIR: Path = ROOT_DIR / "logs"
    SCREENSHOTS_DIR: Path = ROOT_DIR / "screenshots"
    DB_PATH: Path = ROOT_DIR / "database" / "orion.db"

    # ── Speech / Audio ─────────────────────────────────────────────────────────
    SAMPLE_RATE: int = 16_000          # Hz — required by Whisper & openWakeWord
    CHANNELS: int = 1                  # Mono
    CHUNK_SIZE: int = 1_280            # Frames per buffer (80 ms @ 16 kHz)
    RECORD_SECONDS: int = 5            # Max recording length after wake word

    # ── Wake word ──────────────────────────────────────────────────────────────
    WAKE_WORD: str = "hey_jarvis"      # openWakeWord built-in model name
    WAKE_WORD_THRESHOLD: float = 0.5   # Activation sensitivity (0–1)

    # ── Whisper STT ───────────────────────────────────────────────────────────
    # Options: "tiny", "base", "small", "medium", "large"
    # "base" is the recommended starting point (~140 MB, ~3× faster than small)
    WHISPER_MODEL: str = "base"
    WHISPER_LANGUAGE: str = "en"       # Force English decoding (faster)
    WHISPER_DEVICE: str = "cpu"        # "cpu" | "cuda" — switch if GPU available

    # ── Intent confidence thresholds (Operating Rule 5) ───────────────────────
    CONFIDENCE_EXECUTE: float = 0.80   # > 80 % → execute immediately
    CONFIDENCE_CONFIRM: float = 0.50   # 50–80 % → ask user to confirm
    # < CONFIDENCE_CONFIRM           → ask user to clarify

    # ── TTS (pyttsx3) ──────────────────────────────────────────────────────────
    TTS_RATE: int = 180                # Words per minute
    TTS_VOLUME: float = 0.9            # 0.0 – 1.0
    TTS_VOICE_INDEX: int = 0          # 0 = Microsoft David (Male), 1 = Microsoft Zira (Female)

    # ── GUI ────────────────────────────────────────────────────────────────────
    GUI_THEME: str = "dark"            # "dark" | "light" | "system"
    GUI_COLOR_THEME: str = "blue"      # CustomTkinter accent colour

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "DEBUG"
    LOG_TO_FILE: bool = True

    def __init__(self) -> None:
        """Create runtime directories if they don't already exist."""
        for directory in (
            self.LOGS_DIR,
            self.SCREENSHOTS_DIR,
            self.MODELS_DIR,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def __repr__(self) -> str:
        return (
            f"<Settings version={self.VERSION} platform={self.PLATFORM} "
            f"whisper={self.WHISPER_MODEL}>"
        )
