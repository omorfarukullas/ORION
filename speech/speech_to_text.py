"""
speech/speech_to_text.py
========================
Transcribes recorded audio to text using a locally-run Whisper model.
No audio is ever sent to a cloud API (Operating Rule 4).
"""
from __future__ import annotations

import time

import numpy as np
import whisper

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class SpeechToText:
    """
    Wraps OpenAI's Whisper for local, offline speech-to-text transcription.

    Model size is controlled by ``config.settings.Settings.WHISPER_MODEL``.
    Default: ``base`` (~140 MB, fast on CPU).
    """

    def __init__(
        self,
        model_size: str = Settings.WHISPER_MODEL,
        device: str = Settings.WHISPER_DEVICE,
        language: str = Settings.WHISPER_LANGUAGE,
    ) -> None:
        """
        Args:
            model_size: Whisper model size ("tiny", "base", "small", …).
            device:     Inference device ("cpu" or "cuda").
            language:   Language code for decoding (e.g., "en").
        """
        self.model_size = model_size
        self.device = device
        self.language = language
        self._model: whisper.Whisper | None = None  # Loaded lazily on first use

    def load(self) -> None:
        """Download and load the Whisper model into memory."""
        if self._model is not None:
            return

        logger.info(f"Loading Whisper model '{self.model_size}' on device '{self.device}'...")
        start_time = time.time()
        self._model = whisper.load_model(self.model_size, device=self.device)
        elapsed = time.time() - start_time
        logger.info(f"Whisper model '{self.model_size}' loaded successfully in {elapsed:.2f}s.")

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Transcribe a mono float32 audio array.

        Args:
            audio: Mono float32 numpy array at 16 kHz.

        Returns:
            Lowercase stripped transcription string.
        """
        if self._model is None:
            self.load()

        if audio is None or len(audio) == 0:
            logger.warning("Empty or None audio buffer passed to transcribe(). Returning empty string.")
            return ""

        # Ensure input audio is float32
        audio = audio.astype(np.float32)

        logger.info("Transcribing audio...")
        start_time = time.time()
        result = self._model.transcribe(audio, language=self.language, fp16=False)
        elapsed = time.time() - start_time

        transcription = result.get("text", "").strip().lower()
        logger.info(f"Transcription complete in {elapsed:.2f}s: '{transcription}'")
        return transcription
