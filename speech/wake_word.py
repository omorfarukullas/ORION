"""
speech/wake_word.py
===================
Local Wake Word Detector for ORION.

Continuously monitors microphone audio in standby and wakes when the keyword
"ORION" (or variations like "Hey ORION") is detected using a local, lightweight
Whisper model with energy-based Voice Activity Detection gating.
"""
from __future__ import annotations
import re
import threading
import time
from typing import Callable, Optional
import numpy as np
import sounddevice as sd
import whisper

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class WakeWordDetector:
    """
    Listens continuously on the microphone for the keyword "ORION".

    When detected, calls the registered ``on_wake`` callback and returns
    from ``start()`` so the main orchestration loop can prompt the user.
    """

    def __init__(
        self,
        wake_word: str = Settings.WAKE_WORD,
        threshold: float = Settings.WAKE_WORD_THRESHOLD,
        sample_rate: int = Settings.SAMPLE_RATE,
        chunk_size: int = Settings.CHUNK_SIZE,
        chunk_seconds: float = getattr(Settings, "WAKE_WORD_CHUNK_SECONDS", 1.5),
        model_size: str = "tiny",
    ) -> None:
        """
        Args:
            wake_word:     Target keyword (default: "orion").
            threshold:     Unused float kept for API compatibility.
            sample_rate:   Audio sampling rate in Hz (default: 16000).
            chunk_size:    Buffer frame size (default: 1280).
            chunk_seconds: Audio duration per keyword evaluation window (default: 1.5s).
            model_size:    Whisper model size for fast keyword spotting (default: "tiny").
        """
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

    def _is_wake_word_present(self, text: str) -> bool:
        """
        Check if the transcribed text matches the wake word 'orion'.
        """
        if not text:
            return False
        clean = text.lower().strip()
        words = re.findall(r"\b\w+\b", clean)
        # Direct word match or substring match (e.g. 'orion', 'orions', 'hey orion')
        return self.wake_word in words or self.wake_word in clean

    def start(self) -> None:
        """
        Start listening for the wake word (blocking until detected or stopped).
        """
        self.load_model()
        self._stop_event.clear()
        self._is_running = True

        logger.info(
            f"WakeWordDetector active — listening for keyword '{self.wake_word}'..."
        )

        frames_per_window = int(self.sample_rate * self.chunk_seconds)
        audio_buffer: list[np.ndarray] = []
        silence_rms_threshold = 0.015  # Energy threshold to avoid transcribing dead silence

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
                    time.sleep(0.3)

                    # Calculate total collected samples
                    total_samples = sum(len(b) for b in audio_buffer)
                    if total_samples >= frames_per_window:
                        # Grab window and clear buffer
                        window_chunks = list(audio_buffer)
                        audio_buffer.clear()

                        audio_data = np.concatenate(window_chunks, axis=0).flatten()

                        # Quick RMS energy check — skip inference if room is silent
                        rms = float(np.sqrt(np.mean(audio_data ** 2)))
                        if rms < silence_rms_threshold:
                            continue

                        # Transcribe the audio chunk
                        try:
                            result = self._model.transcribe(
                                audio_data,
                                fp16=False,
                                language="en",
                                without_timestamps=True,
                            )
                            transcript = result.get("text", "").strip()
                            if transcript:
                                logger.debug(f"Wake word spotter heard: '{transcript}' (RMS: {rms:.4f})")

                            if self._is_wake_word_present(transcript):
                                logger.info(f"Wake word '{self.wake_word}' detected in transcript: '{transcript}'")
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
