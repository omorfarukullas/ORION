"""
speech/wake_word.py
===================
STUB — Phase 4

Integrates openWakeWord so ORION idles in standby and wakes only when
the configured wake word is detected locally on-device.

Implemented in Phase 4. Do not import this module before then.
"""
from __future__ import annotations
from typing import Callable


class WakeWordDetector:
    """
    Listens continuously on the microphone for the configured wake word.

    When detected, calls the registered ``on_wake`` callback so the main
    loop can hand off to the :class:`speech.listener.Listener`.

    Phase 4 will use openWakeWord's pre-trained ``hey_jarvis`` model
    (rename-able via config). We chose this over Porcupine because it is
    fully open-source with no API key required.
    """

    def __init__(self, wake_word: str = "hey_jarvis", threshold: float = 0.5) -> None:
        """
        Args:
            wake_word:  openWakeWord model name (see config/settings.py).
            threshold:  Activation sensitivity 0–1 (higher = less sensitive).
        """
        self.wake_word = wake_word
        self.threshold = threshold
        self._on_wake: Callable[[], None] | None = None
        raise NotImplementedError("WakeWordDetector is implemented in Phase 4.")

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register the function to call when wake word is detected."""
        self._on_wake = callback

    def start(self) -> None:
        """Start the wake-word detection loop (blocking)."""
        raise NotImplementedError("WakeWordDetector is implemented in Phase 4.")

    def stop(self) -> None:
        """Stop the detection loop gracefully."""
        raise NotImplementedError("WakeWordDetector is implemented in Phase 4.")
