"""
speech/text_to_speech.py
========================
Phase 2 Implementation

Synthesises speech from text using pyttsx3 (offline, cross-platform).
"""

from __future__ import annotations

import pyttsx3
from typing import List, Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class TextToSpeech:
    """
    Wraps pyttsx3 for offline text-to-speech synthesis.

    Uses the OS native TTS engine (SAPI5 on Windows, NSSpeechSynthesizer on macOS,
    espeak on Linux). Fully offline with zero external API dependencies.
    """

    def __init__(self, rate: int = 180, volume: float = 0.9) -> None:
        """
        Args:
            rate:    Words per minute (default: 180).
            volume:  Speech volume 0.0–1.0 (default: 0.9).
        """
        self.rate = rate
        self.volume = volume
        self._engine: Optional[pyttsx3.Engine] = None
        self._init_engine()

    def _init_engine(self) -> None:
        """Initialise the pyttsx3 engine and set properties."""
        try:
            self._engine = pyttsx3.init()
            self.set_rate(self.rate)
            self.set_volume(self.volume)
            logger.info("TextToSpeech engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize TextToSpeech engine: {e}")
            self._engine = None

    def speak(self, text: str) -> None:
        """
        Synthesise and play *text* synchronously.

        Args:
            text: The string to speak aloud.
        """
        if not text or not text.strip():
            return

        logger.info(f"Speaking: '{text}'")
        if self._engine is None:
            logger.warning("TTS engine not initialized; attempting re-initialization.")
            self._init_engine()

        if self._engine:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                logger.error(f"Error during TTS playback: {e}")
        else:
            logger.error("TTS engine unavailable, speech suppressed.")

    def set_rate(self, rate: int) -> None:
        """Change speech rate (words per minute) at runtime."""
        self.rate = rate
        if self._engine:
            try:
                self._engine.setProperty("rate", self.rate)
            except Exception as e:
                logger.warning(f"Could not set TTS rate: {e}")

    def set_volume(self, volume: float) -> None:
        """Change volume at runtime (0.0–1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        if self._engine:
            try:
                self._engine.setProperty("volume", self.volume)
            except Exception as e:
                logger.warning(f"Could not set TTS volume: {e}")

    def list_voices(self) -> List[Dict[str, Any]]:
        """
        Return a list of available system voices.

        Returns:
            List of dicts containing voice ID, Name, and Languages.
        """
        voices_info = []
        if self._engine:
            try:
                voices = self._engine.getProperty("voices")
                for index, voice in enumerate(voices):
                    voices_info.append(
                        {
                            "index": index,
                            "id": voice.id,
                            "name": voice.name,
                            "languages": getattr(voice, "languages", []),
                        }
                    )
            except Exception as e:
                logger.error(f"Error listing voices: {e}")
        return voices_info

    def set_voice_by_index(self, index: int) -> bool:
        """Set the active voice by index."""
        if self._engine:
            try:
                voices = self._engine.getProperty("voices")
                if 0 <= index < len(voices):
                    self._engine.setProperty("voice", voices[index].id)
                    logger.info(f"TTS voice set to: {voices[index].name}")
                    return True
                else:
                    logger.warning(f"Voice index {index} out of range.")
            except Exception as e:
                logger.error(f"Error setting voice index: {e}")
        return False
