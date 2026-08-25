"""
ORION — Operational Responsive Intelligent Orchestration Network
================================================================
Entry point. Bootstraps the system, checks dependencies, initializes
components, and starts the GUI and voice orchestration loops.
"""

from __future__ import annotations
import sys
import os
import threading
from typing import Any

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


def voice_orchestration_loop(
    settings: Settings,
    tts: Any,
    stt: Any,
    listener: Any,
    detector: Any,
    command_parser: Any,
    task_planner: Any,
    confirmation_handler: Any,
    context: Any,
    db: Any,
    dashboard: Any = None,
) -> None:
    """
    Main voice interaction standby loop.
    """
    logger.info("ORION ready. Entering continuous standby loop. Press Ctrl+C to exit.")

    try:
        while True:
            if dashboard:
                dashboard.update_status("IDLE")
            logger.info(f"Standby — listening for wake word '{settings.WAKE_WORD}'...")
            detector.start()

            if dashboard:
                dashboard.update_status("LISTENING")
            logger.info("Wake word triggered! Prompting user and recording command...")
            tts.speak("Yes?")

            audio = listener.record()

            if len(audio) > 0:
                if dashboard:
                    dashboard.update_status("PROCESSING")
                transcript = stt.transcribe(audio)
                logger.info(f"Final Transcript: '{transcript}'")
                if transcript:
                    # Check for multi-step tasks (Phase 12)
                    if task_planner and task_planner.is_multi_step(transcript):
                        steps = task_planner.plan(transcript)
                        reply = task_planner.execute_plan(
                            steps=steps,
                            dispatch_fn=dispatch,
                            confirmation_handler=confirmation_handler,
                            context=context,
                            db=db,
                        )
                        primary_intent = "MULTI_STEP"
                        primary_conf = 1.0
                        entities_summary = {"steps": len(steps)}
                    else:
                        parsed_cmd = command_parser.parse(transcript)
                        resolved_cmd = context.resolve(parsed_cmd)
                        reply = dispatch(
                            resolved_cmd,
                            confirmation_handler=confirmation_handler,
                            db=db,
                        )
                        context.update(resolved_cmd)
                        db.log_command(
                            raw_text=transcript,
                            intent=resolved_cmd.intent,
                            confidence=resolved_cmd.confidence,
                            entities=resolved_cmd.entities,
                            outcome=reply,
                        )
                        primary_intent = resolved_cmd.intent
                        primary_conf = resolved_cmd.confidence
                        entities_summary = resolved_cmd.entities

                    # Update GUI Dashboard (Phase 10)
                    if dashboard:
                        dashboard.update_command(
                            raw_text=transcript,
                            intent=primary_intent,
                            confidence=primary_conf,
                            entities=entities_summary,
                            outcome=reply,
                        )

                    logger.info(f"Command execution reply: '{reply}'")
                    if dashboard:
                        dashboard.update_status("SPEAKING")
                    tts.speak(reply)
                else:
                    if dashboard:
                        dashboard.update_status("SPEAKING")
                    tts.speak("I did not hear any speech.")
            else:
                logger.warning("No audio recorded.")

            if dashboard:
                dashboard.update_status("IDLE")

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Shutting down ORION...")
        detector.stop()
        tts.speak("Goodbye.")


def main() -> None:
    """Bootstrap ORION and start GUI and orchestration loop."""
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

    # ── Phase 5-12: NLP, Planner, Security, Context, Memory & Database ──────────
    from nlp.command_parser import CommandParser
    from nlp.command_dispatcher import dispatch
    from planner.task_planner import TaskPlanner
    from security.confirmation import ConfirmationHandler
    from planner.context import ConversationContext
    from database.database import Database

    command_parser = CommandParser()
    task_planner = TaskPlanner(command_parser=command_parser)
    confirmation_handler = ConfirmationHandler(tts=tts, listener=listener, stt=stt)
    context = ConversationContext()
    db = Database(settings.DB_PATH)

    # ── Phase 10: GUI Dashboard ─────────────────────────────────────────────────
    dashboard = None
    try:
        from gui.dashboard import launch_dashboard
        dashboard = launch_dashboard()
        logger.info("GUI Dashboard initialized.")
    except Exception as e:
        logger.warning(f"Could not initialize GUI Dashboard ({e}). Running in headless console mode.")

    # Start voice orchestration in a background daemon thread if GUI is active
    if dashboard is not None:
        backend_thread = threading.Thread(
            target=voice_orchestration_loop,
            args=(
                settings,
                tts,
                stt,
                listener,
                detector,
                command_parser,
                task_planner,
                confirmation_handler,
                context,
                db,
                dashboard,
            ),
            daemon=True,
        )
        backend_thread.start()
        # Main thread runs CustomTkinter GUI loop
        try:
            dashboard.run()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received from GUI loop. Shutting down ORION...")
    else:
        # Run directly on main thread if headless
        try:
            voice_orchestration_loop(
                settings,
                tts,
                stt,
                listener,
                detector,
                command_parser,
                task_planner,
                confirmation_handler,
                context,
                db,
                None,
            )
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Shutting down ORION...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ORION] Exited cleanly.")
