"""
actions/media.py
================
STUB — Phase 8

Media playback controls (play, pause, next/previous track, volume,
mute) using pyautogui virtual key presses (cross-platform media keys).
"""
from __future__ import annotations


def play_pause() -> str:
    """Toggle play/pause on the active media player."""
    raise NotImplementedError("play_pause is implemented in Phase 8.")


def next_track() -> str:
    """Skip to the next track."""
    raise NotImplementedError("next_track is implemented in Phase 8.")


def previous_track() -> str:
    """Go back to the previous track."""
    raise NotImplementedError("previous_track is implemented in Phase 8.")


def volume_up(steps: int = 5) -> str:
    """Increase system volume by *steps* key presses."""
    raise NotImplementedError("volume_up is implemented in Phase 8.")


def volume_down(steps: int = 5) -> str:
    """Decrease system volume by *steps* key presses."""
    raise NotImplementedError("volume_down is implemented in Phase 8.")


def mute() -> str:
    """Toggle system mute."""
    raise NotImplementedError("mute is implemented in Phase 8.")
