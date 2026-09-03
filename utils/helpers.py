"""
utils/helpers.py
================
Miscellaneous utility helpers used across ORION modules.

Implemented in Phase 1 as fully working utilities (not stubs), since
these are pure-Python helpers with no external dependencies.
"""

import datetime
import re
import time

# ── Text helpers ──────────────────────────────────────────────────────────────

def normalise_text(text: str) -> str:
    """
    Lowercase, strip leading/trailing whitespace, collapse multiple spaces,
    and remove punctuation that would confuse the intent classifier.

    Args:
        text: Raw transcribed string from Whisper.

    Returns:
        Cleaned string ready for NLP processing.
    """
    text = text.lower().strip()
    # Remove punctuation except apostrophes (e.g. "don't")
    text = re.sub(r"[^\w\s']", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_wake_word(text: str, wake_word: str = "orion") -> str:
    """
    Strip the wake-word prefix from a transcribed command so the intent
    classifier sees "open chrome" rather than "orion open chrome".

    Args:
        text:      Normalised command string.
        wake_word: The wake word to remove (default: "orion").

    Returns:
        String with wake-word prefix removed.
    """
    pattern = rf"^\s*{re.escape(wake_word)}\s*,?\s*"
    return re.sub(pattern, "", text, flags=re.IGNORECASE).strip()


# ── Time / date helpers ───────────────────────────────────────────────────────

def get_current_time() -> str:
    """Return human-readable current time, e.g. '3:42 PM'."""
    return datetime.datetime.now().strftime("%-I:%M %p") if hasattr(time, "struct_time") else \
           datetime.datetime.now().strftime("%I:%M %p").lstrip("0")


def get_current_date() -> str:
    """Return human-readable current date, e.g. 'Wednesday, August 13, 2026'."""
    return datetime.datetime.now().strftime("%A, %B %d, %Y")


# ── Misc ──────────────────────────────────────────────────────────────────────

def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp *value* to the range [minimum, maximum]."""
    return max(minimum, min(value, maximum))


def truncate(text: str, max_len: int = 80, suffix: str = "…") -> str:
    """Truncate *text* to *max_len* characters, appending *suffix* if cut."""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def format_bytes(num_bytes: int) -> str:
    """Format a byte count as a human-readable string (e.g. '1.4 GB')."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes //= 1024  # type: ignore[assignment]
    return f"{num_bytes:.1f} PB"
