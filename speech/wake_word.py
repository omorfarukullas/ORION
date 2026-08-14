"""
speech/wake_word.py
===================
Integrates openWakeWord so ORION idles in standby and wakes only when
the configured wake word is detected locally on-device.
"""
from __future__ import annotations
import threading
import time
from typing import Callable
import numpy as np
import sounddevice as sd

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class WakeWordDetector:
    """
    Listens continuously on the microphone for the configured wake word.

    When detected, calls the registered ``on_wake`` callback so the main
    loop can hand off to the :class:`speech.listener.Listener`.
    """

    def __init__(
        self,
        wake_word: str = Settings.WAKE_WORD,
        threshold: float = Settings.WAKE_WORD_THRESHOLD,
        sample_rate: int = Settings.SAMPLE_RATE,
        chunk_size: int = Settings.CHUNK_SIZE,
    ) -> None:
        """
        Args:
            wake_word:   openWakeWord model name (default: "hey_jarvis").
            threshold:   Activation sensitivity 0–1 (default: 0.5).
            sample_rate: Audio sampling rate in Hz (default: 16000).
            chunk_size:  Frames per audio chunk (default: 1280, ~80ms @ 16kHz).
        """
        self.wake_word = wake_word
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._on_wake: Callable[[], None] | None = None
        self._model = None
        self._is_running = False
        self._stop_event = threading.Event()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register the function to call when wake word is detected."""
        self._on_wake = callback

    def load_model(self) -> None:
        """Lazy load openWakeWord model into memory."""
        if self._model is not None:
            return

        logger.info(f"Loading openWakeWord model '{self.wake_word}'...")
        import openwakeword
        from openwakeword.model import Model

        openwakeword.utils.download_models()
        self._model = Model(wakeword_models=[self.wake_word], inference_framework="onnx")
        logger.info(f"openWakeWord model '{self.wake_word}' loaded successfully.")

    def start(self) -> None:
        """
        Start listening for the wake word (blocking until detected or stopped).
        """
        self.load_model()
        self._stop_event.clear()
        self._is_running = True

        logger.info(
            f"WakeWordDetector active — listening for '{self.wake_word}' (threshold={self.threshold})..."
        )

        def audio_callback(indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
            if status:
                logger.warning(f"Audio callback status warning: {status}")
            if not self._is_running or self._stop_event.is_set():
                return

            chunk = indata.flatten()
            prediction = self._model.predict(chunk)

            score = 0.0
            if isinstance(prediction, dict):
                score = prediction.get(self.wake_word, 0.0)
                if self.wake_word not in prediction:
                    for key, val in prediction.items():
                        if self.wake_word in key:
                            score = val
                            break

            if score >= self.threshold:
                logger.info(
                    f"Wake word '{self.wake_word}' detected with score {score:.3f} >= threshold {self.threshold}"
                )
                self._stop_event.set()
                if self._on_wake:
                    self._on_wake()

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=self.chunk_size,
            callback=audio_callback,
        ):
            while not self._stop_event.is_set():
                time.sleep(0.05)

        self._is_running = False
        logger.info("WakeWordDetector loop ended.")

    def stop(self) -> None:
        """Stop the detection loop gracefully."""
        self._stop_event.set()
        self._is_running = False
