"""
config/settings.py
==================
Central configuration for ORION.

All tuneable knobs live here so that no magic numbers are scattered
across the codebase. Import with:

    from config.settings import Settings
    s = Settings()
"""

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

    # ── VAD (Voice Activity Detection) ────────────────────────────────────────────
    VAD_SILENCE_THRESHOLD: float = 0.005  # RMS amplitude below which = silence
    VAD_SILENCE_DURATION: float = 1.5     # Seconds of silence to trigger stop

    # ── Wake word ──────────────────────────────────────────────────────────────
    WAKE_WORD: str = "orion"           # Wake word keyword name
    WAKE_WORD_THRESHOLD: float = 0.5   # Activation sensitivity (0–1)
    WAKE_WORD_CHUNK_SECONDS: float = 1.5  # Seconds of audio per detection window
    WAKE_WORD_MODEL: str = "tiny"        # Whisper model size for wake word detection

    # ── Local Ollama LLM ──────────────────────────────────────────────────────
    OLLAMA_ENABLED: bool = True
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    LLM_MAX_TOKENS: int = 250

    # ── Whisper STT ───────────────────────────────────────────────────────────
    # Options: "tiny", "base", "small", "medium", "large"
    # "base" is the recommended starting point (~140 MB, ~3× faster than small)
    WHISPER_MODEL: str = "base"
    WHISPER_LANGUAGE: str = "en"       # Force English decoding (faster)
    WHISPER_DEVICE: str = "cpu"        # "cpu" | "cuda" — switch if GPU available

    # ── Intent confidence thresholds (Operating Rule 5) ───────────────────────
    CONFIDENCE_EXECUTE: float = 0.70   # > 70 % → execute immediately (recalibrated for vector similarity)
    CONFIDENCE_CONFIRM: float = 0.45   # 45–70 % → ask user to confirm
    # < CONFIDENCE_CONFIRM           → ask user to clarify

    # ── TTS (pyttsx3) & Voice Personas ─────────────────────────────────────────
    TTS_RATE: int = 180                # Words per minute
    TTS_VOLUME: float = 0.9            # 0.0 – 1.0
    TTS_VOICE_INDEX: int = 0          # 0 = Microsoft David (Male), 1 = Microsoft Zira (Female)
    VOICE_PERSONA: str = "professional"  # "professional" | "friendly" | "coqui_clone"

    # ── Web Dashboard & REST / WebSocket API ───────────────────────────────────
    WEB_ENABLED: bool = True
    WEB_HOST: str = "127.0.0.1"
    WEB_PORT: int = 8080

    # ── Cloud Plugin Registry ──────────────────────────────────────────────────
    PLUGIN_REGISTRY_URL: str = "https://raw.githubusercontent.com/omorfarukullas/ORION-plugins/main/index.json"

    # ── GUI ────────────────────────────────────────────────────────────────────
    GUI_THEME: str = "dark"            # "dark" | "light" | "system"
    GUI_COLOR_THEME: str = "blue"      # CustomTkinter accent colour

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "DEBUG"
    LOG_TO_FILE: bool = True

    USER_SETTINGS_PATH: Path = CONFIG_DIR / "user_settings.json"

    def __init__(self) -> None:
        """Create runtime directories if they don't already exist and load user settings overrides."""
        for directory in (
            self.LOGS_DIR,
            self.SCREENSHOTS_DIR,
            self.MODELS_DIR,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        self.load_user_settings()

    @classmethod
    def load_user_settings(cls) -> None:
        """Load user overrides from config/user_settings.json if present."""
        if cls.USER_SETTINGS_PATH.exists():
            try:
                import json
                with open(cls.USER_SETTINGS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for key, value in data.items():
                    if hasattr(cls, key):
                        setattr(cls, key, value)
            except Exception:
                pass

    @classmethod
    def save_user_settings(cls) -> None:
        """Save current user settings to config/user_settings.json."""
        import json
        settings_dict = {
            "CONFIDENCE_EXECUTE": cls.CONFIDENCE_EXECUTE,
            "CONFIDENCE_CONFIRM": cls.CONFIDENCE_CONFIRM,
            "OLLAMA_ENABLED": cls.OLLAMA_ENABLED,
            "TTS_RATE": cls.TTS_RATE,
            "GUI_THEME": cls.GUI_THEME,
            "VOICE_PERSONA": cls.VOICE_PERSONA,
            "WEB_ENABLED": cls.WEB_ENABLED,
            "WEB_PORT": cls.WEB_PORT,
        }
        try:
            with open(cls.USER_SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(settings_dict, f, indent=2)
        except Exception:
            pass

    def __repr__(self) -> str:
        return (
            f"<Settings version={self.VERSION} platform={self.PLATFORM} "
            f"whisper={self.WHISPER_MODEL}>"
        )
