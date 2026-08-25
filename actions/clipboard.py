"""
actions/clipboard.py
====================
System clipboard manager (read, copy, clear) using pyperclip.
"""
from __future__ import annotations
import pyperclip
from utils.logger import get_logger

logger = get_logger(__name__)


def read_clipboard() -> str:
    """Read and return current text in system clipboard."""
    try:
        content = pyperclip.paste().strip()
        if not content:
            return "Your clipboard is currently empty."

        # Limit spoken text length
        truncated = content[:200] + ("..." if len(content) > 200 else "")
        logger.info(f"Read clipboard ({len(content)} chars): '{truncated}'")
        return f"Your clipboard contains: {truncated}"
    except Exception as e:
        logger.error(f"Failed to read clipboard: {e}")
        return "Could not read clipboard contents."


def copy_to_clipboard(text: str) -> str:
    """Copy *text* to system clipboard."""
    if not text:
        return "What would you like me to copy?"

    try:
        pyperclip.copy(text)
        logger.info(f"Copied to clipboard: '{text}'")
        return f"Copied '{text}' to clipboard."
    except Exception as e:
        logger.error(f"Failed to copy to clipboard: {e}")
        return "Failed to copy text to clipboard."


def clear_clipboard() -> str:
    """Clear system clipboard."""
    try:
        pyperclip.copy("")
        logger.info("Clipboard cleared.")
        return "Clipboard cleared."
    except Exception as e:
        logger.error(f"Failed to clear clipboard: {e}")
        return "Failed to clear clipboard."
