"""
speech/wake_word.py
===================
Local Wake Word Detector for ORION.

Continuously monitors microphone audio in standby and wakes when the keyword
"ORION" (or phonetic variations) is detected, or when a direct voice command
is recognized, using a local Whisper model with sliding-window Voice Activity Detection.
"""
from __future__ import annotations
import re
import threading
import time
from typing import Callable, Optional, Tuple
import numpy as np
import sounddevice as sd
import whisper

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class WakeWordDetector:
    """
    Listens continuously on the microphone for the keyword "ORION" or direct commands.

    Supports both:
    1. Call & Response: User says "ORION" -> triggers wake-up, returns empty command -> ORION asks "Yes?"
    2. Single-Breath / Direct Command: User says "ORION open notepad" or "what time is it" -> extracts command immediately.
    """

    # Common phonetic or spelling variations output by Whisper
    WAKE_WORD_ALIASES = {
        "orion",
        "orian",
        "orean",
        "aurion",
        "orien",
        "orient",
        "orions",
        "o'rion",
        "o-rion",
        "aryan",
        "ryan",
        "o ryan",
        "o'ryan",
        "arian",
        "iron",
        "horion",
    }

    # Direct command starter prefixes
    COMMAND_STARTERS = [
        "open ",
        "launch ",
        "start ",
        "close ",
        "quit ",
        "exit ",
        "search ",
        "google ",
        "youtube ",
        "what ",
        "tell me ",
        "how much ",
        "check ",
        "take a screenshot",
        "screenshot",
        "capture screen",
        "play ",
        "pause",
        "resume",
        "mute",
        "unmute",
        "volume ",
        "create ",
        "delete ",
        "find ",
        "remember ",
        "recall ",
        "shut down",
        "restart ",
    ]

    def __init__(
        self,
        wake_word: str = Settings.WAKE_WORD,
        threshold: float = Settings.WAKE_WORD_THRESHOLD,
        sample_rate: int = Settings.SAMPLE_RATE,
        chunk_size: int = Settings.CHUNK_SIZE,
        chunk_seconds: float = 2.0,
        model_size: str = Settings.WAKE_WORD_MODEL,
    ) -> None:
        self.wake_word = wake_word.lower()
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.chunk_seconds = chunk_seconds
        self.model_size = model_size

        self._on_wake: Optional[Callable[[], None]] = None
        self._model = None
        self._is_running = False
        self._stop_event = threading.Event()
        self.last_detected_command: str = ""

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register the function to call when wake word is detected."""
        self._on_wake = callback

    def load_model(self) -> None:
        """Lazy load Whisper model into memory."""
        if self._model is not None:
            return

        logger.info(f"Loading local Whisper wake word model '{self.model_size}'...")
        self._model = whisper.load_model(self.model_size, device="cpu")
        logger.info(f"Local Whisper wake word model '{self.model_size}' loaded successfully.")

    def _strip_wake_word(self, text: str) -> str:
        """Remove wake word prefixes (e.g. 'hey orion', 'orion') from transcript."""
        cleaned = text.strip()
        # Regex to strip common prefixes
        pattern = rf"^(?:hey\s+|hi\s+|ok\s+|hello\s+)?(?:{'|'.join(re.escape(w) for w in self.WAKE_WORD_ALIASES)})\s*[,.:;]?\s*"
        remainder = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
        return remainder

    def _is_wake_word_present(self, text: str) -> Tuple[bool, str]:
        """
        Check if the transcribed text matches the wake word or direct commands.

        Returns:
            (is_wake_detected, extracted_command_or_empty)
        """
        if not text:
            return (False, "")

        clean = text.lower().strip()
        words = set(re.findall(r"\b\w+\b", clean))

        # Check for wake word / phonetic aliases
        has_wake_word = (
            self.wake_word in clean
            or bool(words.intersection(self.WAKE_WORD_ALIASES))
        )

        if has_wake_word:
            remainder = self._strip_wake_word(text)
            logger.info(f"Wake word detected! Remainder command: '{remainder}'")
            return (True, remainder)

        return (False, "")

    def get_detected_command(self) -> str:
        """Retrieve any command captured during the wake word detection window."""
        cmd = self.last_detected_command
        self.last_detected_command = ""
        return cmd

    def start(self) -> None:
        """
        Start listening for the wake word (blocking until detected or stopped).
        Uses a sliding rolling buffer for seamless real-time detection.
        """
        self.load_model()
        self._stop_event.clear()
        self._is_running = True
        self.last_detected_command = ""

        logger.info(
            f"WakeWordDetector active — listening for keyword '{self.wake_word}' or direct commands..."
        )

        max_buffer_samples = int(self.sample_rate * self.chunk_seconds)
        audio_buffer: list[np.ndarray] = []
        silence_rms_threshold = 0.005
        last_eval_time = time.time()
        eval_interval = 0.4  # Re-evaluate every 400ms

        def audio_callback(indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
            if status:
                logger.debug(f"Audio callback status: {status}")
            if not self._is_running or self._stop_event.is_set():
                return
            audio_buffer.append(indata.copy())

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self.chunk_size,
                callback=audio_callback,
            ):
                while not self._stop_event.is_set():
                    time.sleep(0.08)

                    now = time.time()
                    if now - last_eval_time < eval_interval:
                        continue

                    # Maintain rolling window of maximum `chunk_seconds`
                    total_samples = sum(len(b) for b in audio_buffer)
                    min_samples = min(int(self.sample_rate * 0.7), max_buffer_samples)
                    if total_samples < min_samples:
                        continue

                    while total_samples > max_buffer_samples and len(audio_buffer) > 1:
                        removed = audio_buffer.pop(0)
                        total_samples -= len(removed)

                    audio_data = np.concatenate(list(audio_buffer), axis=0).flatten()

                    # RMS energy check — skip inference if room is quiet
                    rms = float(np.sqrt(np.mean(audio_data ** 2)))
                    if rms < silence_rms_threshold:
                        last_eval_time = now
                        continue

                    last_eval_time = now

                    # Transcribe the audio chunk with Whisper
                    try:
                        result = self._model.transcribe(
                            audio_data,
                            fp16=False,
                            language="en",
                            without_timestamps=True,
                        )
                        transcript = result.get("text", "").strip()
                        if transcript:
                            logger.info(f"Hearing: '{transcript}' (RMS: {rms:.4f})")

                        is_detected, cmd = self._is_wake_word_present(transcript)
                        if is_detected:
                            logger.info(f"Wake detection triggered! Command: '{cmd}'")
                            self.last_detected_command = cmd
                            self._stop_event.set()
                            if self._on_wake:
                                self._on_wake()
                            break
                    except Exception as e:
                        logger.error(f"Error during wake word transcription: {e}")

        except Exception as e:
            logger.error(f"InputStream error in WakeWordDetector: {e}")
        finally:
            self._is_running = False
            logger.info("WakeWordDetector standby loop ended.")

    def stop(self) -> None:
        """Stop the detection loop gracefully."""
        self._stop_event.set()
        self._is_running = False
