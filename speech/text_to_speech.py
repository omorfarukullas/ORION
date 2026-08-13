"""
speech/text_to_speech.py
========================
STUB — Phase 2

Synthesises speech from text using pyttsx3 (offline, cross-platform).
"""
from __future__ import annotations


class TextToSpeech:
    """
    Wraps pyttsx3 for offline text-to-speech synthesis.

    Phase 2 will initialise the engine, set rate/volume from settings,
    and expose a blocking ``speak()`` method and an async ``speak_async()``
    method for non-blocking use once the main loop exists.

    Trade-off: pyttsx3 uses the OS native TTS engine (SAPI5 on Windows,
    NSSpeechSynthesizer on macOS, espeak on Linux). It is not as natural
    as neural TTS but works entirely offline with zero configuration.
    """

    def __init__(self, rate: int = 180, volume: float = 0.9) -> None:
        """
        Args:
            rate:    Words per minute.
            volume:  Speech volume 0.0–1.0.
        """
        self.rate = rate
        self.volume = volume

    def speak(self, text: str) -> None:
        """
        Synthesise and play *text* synchronously.

        Args:
            text: The string to speak aloud.

        Raises:
            NotImplementedError: Until Phase 2 is implemented.
        """
        raise NotImplementedError("TextToSpeech is implemented in Phase 2.")

    def set_rate(self, rate: int) -> None:
        """Change speech rate at runtime."""
        raise NotImplementedError("TextToSpeech is implemented in Phase 2.")

    def set_volume(self, volume: float) -> None:
        """Change volume at runtime (0.0–1.0)."""
        raise NotImplementedError("TextToSpeech is implemented in Phase 2.")
