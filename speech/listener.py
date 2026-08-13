"""
speech/listener.py
==================
STUB — Phase 3

Handles microphone recording after wake-word detection. Captures audio
until silence is detected or ``max_seconds`` elapses, then returns the
raw audio buffer for transcription.
"""
from __future__ import annotations
import numpy as np


class Listener:
    """
    Records a single command from the microphone.

    Triggered by :class:`speech.wake_word.WakeWordDetector` after wake
    word confirmation. Uses ``sounddevice`` for cross-platform mic input
    at 16 kHz (required by both openWakeWord and Whisper).

    Phase 3 will add VAD (Voice Activity Detection) using Whisper's own
    silence detection to know when the user has finished speaking.
    """

    def __init__(self, sample_rate: int = 16_000, max_seconds: int = 5) -> None:
        """
        Args:
            sample_rate:  Audio sample rate in Hz (must be 16 000 for Whisper).
            max_seconds:  Maximum recording duration before auto-stop.
        """
        self.sample_rate = sample_rate
        self.max_seconds = max_seconds

    def record(self) -> np.ndarray:
        """
        Record audio from the default microphone.

        Returns:
            Mono float32 numpy array at ``self.sample_rate`` Hz.

        Raises:
            NotImplementedError: Until Phase 3 is implemented.
        """
        raise NotImplementedError("Listener is implemented in Phase 3.")
