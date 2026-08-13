"""
security/confirmation.py
========================
STUB — Phase 9

Spoken/GUI confirmation dialog for destructive actions.

For destructive intents, ORION speaks "You asked me to [action].
Should I continue?" and listens for an explicit "yes" before proceeding.
"""
from __future__ import annotations


class ConfirmationHandler:
    """
    Asks the user to confirm a destructive action before execution.

    Phase 9 implementation:
        1. TTS speaks the confirmation question.
        2. Listener records the response (short timeout: 5 seconds).
        3. Whisper transcribes; if "yes" → return True, else → return False.
    """

    def ask(self, action_description: str) -> bool:
        """
        Ask the user to confirm *action_description*.

        Args:
            action_description: Human-readable description of the action,
                e.g. "delete the file old.txt".

        Returns:
            True if the user confirms, False otherwise.

        Raises:
            NotImplementedError: Until Phase 9 is implemented.
        """
        raise NotImplementedError("ConfirmationHandler is implemented in Phase 9.")
