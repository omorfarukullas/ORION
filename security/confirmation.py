"""
security/confirmation.py
========================
Phase 9 — Spoken & Text Confirmation Handler

For destructive intents, ORION asks "You asked me to [action]. Should I continue?"
and listens for an explicit "yes" before proceeding.
"""
from __future__ import annotations
from typing import Any
from utils.logger import get_logger

logger = get_logger(__name__)


class ConfirmationHandler:
    """
    Asks the user to confirm a destructive action before execution.
    """

    def __init__(self, tts: Any = None, listener: Any = None, stt: Any = None) -> None:
        self.tts = tts
        self.listener = listener
        self.stt = stt

    def ask(self, action_description: str) -> bool:
        """
        Ask the user to confirm *action_description*.

        Args:
            action_description: Human-readable description of the action,
                e.g. "delete the file old.txt".

        Returns:
            True if the user confirms with 'yes', False otherwise.
        """
        prompt = f"You asked me to {action_description}. Should I continue?"
        logger.warning(f"Requesting user confirmation for: '{action_description}'")

        if self.tts:
            self.tts.speak(prompt)

        if self.listener and self.stt:
            logger.info("Recording confirmation response (up to 5 seconds)...")
            audio = self.listener.record()
            if len(audio) > 0:
                response = self.stt.transcribe(audio).lower().strip()
                logger.info(f"User confirmation response: '{response}'")
                if "yes" in response or "yeah" in response or "confirm" in response or "do it" in response:
                    logger.info("User CONFIRMED the action.")
                    return True
            logger.info("User did NOT confirm the action.")
            return False
        else:
            # Fallback for testing or headless execution: deny by default
            logger.warning("No audio components provided to ConfirmationHandler. Action cancelled by default.")
            return False
