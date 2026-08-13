"""
speech/speech_to_text.py
========================
STUB — Phase 3

Transcribes recorded audio to text using a locally-run Whisper model.
No audio is ever sent to a cloud API (Operating Rule 4).
"""
from __future__ import annotations
import numpy as np


class SpeechToText:
    """
    Wraps OpenAI's Whisper for local, offline speech-to-text transcription.

    Model size is controlled by ``config.settings.Settings.WHISPER_MODEL``.
    Default: ``base`` (~140 MB, fast on CPU).

    Phase 3 trade-off: We use ``openai-whisper`` (pure Python) rather than
    ``faster-whisper`` because it has fewer binary dependencies and works
    out-of-the-box on Windows without CUDA. Switch to ``faster-whisper``
    in a later phase if latency becomes a problem.
    """

    def __init__(self, model_size: str = "base", device: str = "cpu") -> None:
        """
        Args:
            model_size:  Whisper model size ("tiny", "base", "small", …).
            device:      Inference device ("cpu" or "cuda").
        """
        self.model_size = model_size
        self.device = device
        self._model = None  # Loaded lazily on first use

    def load(self) -> None:
        """Download and load the Whisper model into memory."""
        raise NotImplementedError("SpeechToText is implemented in Phase 3.")

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Transcribe a mono float32 audio array.

        Args:
            audio: Mono float32 numpy array at 16 kHz.

        Returns:
            Lowercase stripped transcription string.

        Raises:
            NotImplementedError: Until Phase 3 is implemented.
        """
        raise NotImplementedError("SpeechToText is implemented in Phase 3.")
