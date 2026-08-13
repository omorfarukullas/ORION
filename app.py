"""
ORION — Operational Responsive Intelligent Orchestration Network
================================================================
Entry point. Bootstraps the system, checks dependencies, and
starts the main orchestration loop.

Phase 1: Scaffold + initialization only.
         Later phases wire in the real pipeline here.
"""

import sys
import os

# ── Ensure project root is on sys.path regardless of CWD ──────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Internal imports ───────────────────────────────────────────────────────────
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


def check_python_version() -> None:
    """Abort early if Python version is below the minimum."""
    if sys.version_info < (3, 11):
        print(
            f"[ORION] ERROR: Python 3.11+ is required. "
            f"You are running {sys.version}. Please upgrade."
        )
        sys.exit(1)


def main() -> None:
    """Bootstrap ORION and hand off to the orchestration loop."""
    check_python_version()

    settings = Settings()

    logger.info("=" * 60)
    logger.info("  ORION — Operational Responsive Intelligent Orchestration Network")
    logger.info(f"  Version : {settings.VERSION}")
    logger.info(f"  Platform: {settings.PLATFORM}")
    logger.info(f"  Whisper : {settings.WHISPER_MODEL}")
    logger.info("=" * 60)

    print("\n  ORION initialized.\n")

    # ── Phase 2: Text-to-speech initialization & greeting ──────────────────────
    from speech.text_to_speech import TextToSpeech
    tts = TextToSpeech(rate=settings.TTS_RATE, volume=settings.TTS_VOLUME)
    tts.speak("Hello. I am ORION.")

    # ── Placeholder: future phases hook in here ────────────────────────────────
    # Phase 3  → from speech.listener import Listener; listener.start()
    # Phase 4  → from speech.wake_word import WakeWordDetector; wwd.run()
    # Phase 5+ → from planner.task_planner import TaskPlanner; planner.run()


if __name__ == "__main__":
    main()
