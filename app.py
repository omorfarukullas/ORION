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

    # ── Phase 2: Speech Output ──────────────────────────────────────────────────
    from speech.text_to_speech import TextToSpeech
    tts = TextToSpeech(
        rate=settings.TTS_RATE,
        volume=settings.TTS_VOLUME,
        voice_index=settings.TTS_VOICE_INDEX,
    )
    tts.speak("Hello. I am ORION.")

    # ── Phase 3: Speech Input (STT & Listener) ──────────────────────────────────
    from speech.listener import Listener
    from speech.speech_to_text import SpeechToText

    stt = SpeechToText(
        model_size=settings.WHISPER_MODEL,
        device=settings.WHISPER_DEVICE,
        language=settings.WHISPER_LANGUAGE,
    )
    stt.load()

    listener = Listener(
        sample_rate=settings.SAMPLE_RATE,
        max_seconds=settings.RECORD_SECONDS,
        silence_threshold=settings.VAD_SILENCE_THRESHOLD,
        silence_duration=settings.VAD_SILENCE_DURATION,
        chunk_size=settings.CHUNK_SIZE,
    )

    # ── Phase 4: Wake Word Standby Loop ─────────────────────────────────────────
    from speech.wake_word import WakeWordDetector

    detector = WakeWordDetector(
        wake_word=settings.WAKE_WORD,
        threshold=settings.WAKE_WORD_THRESHOLD,
        sample_rate=settings.SAMPLE_RATE,
        chunk_size=settings.CHUNK_SIZE,
    )

    # ── Phase 5 & 6: Intent Classification & Command Engine ────────────────────
    from nlp.rule_engine import RuleEngine
    from nlp.intent_classifier import IntentClassifier
    from nlp.command_dispatcher import dispatch, dispatch_with_confidence

    rule_engine = RuleEngine()
    classifier = IntentClassifier()

    use_ml = False
    try:
        classifier.load()
        use_ml = True
        logger.info("Using Phase 6 ML IntentClassifier.")
    except Exception as e:
        logger.warning(f"Could not load ML IntentClassifier ({e}). Falling back to Phase 5 RuleEngine.")

    logger.info("ORION ready. Entering continuous standby loop. Press Ctrl+C to exit.")

    try:
        while True:
            logger.info(f"Standby — listening for wake word '{settings.WAKE_WORD}'...")
            detector.start()

            logger.info("Wake word triggered! Prompting user and recording command...")
            tts.speak("Yes?")

            audio = listener.record()

            if len(audio) > 0:
                transcript = stt.transcribe(audio)
                logger.info(f"Final Transcript: '{transcript}'")
                if transcript:
                    if use_ml:
                        intent, confidence = classifier.predict(transcript)
                        rule_cmd = rule_engine.parse(transcript)
                        reply = dispatch_with_confidence(intent, confidence, rule_cmd.entity, transcript)
                    else:
                        cmd = rule_engine.parse(transcript)
                        reply = dispatch(cmd)

                    logger.info(f"Command execution reply: '{reply}'")
                    tts.speak(reply)
                else:
                    tts.speak("I did not hear any speech.")
            else:
                logger.warning("No audio recorded.")

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Shutting down ORION...")
        detector.stop()
        tts.speak("Goodbye.")


if __name__ == "__main__":
    main()
