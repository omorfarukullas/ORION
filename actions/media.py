"""
actions/media.py
================
Media playback controls using pyautogui virtual key presses.
"""
from __future__ import annotations
import pyautogui
from utils.logger import get_logger

logger = get_logger(__name__)


def play_media() -> str:
    """Start/resume media playback."""
    logger.info("Pressing virtual key 'playpause'")
    pyautogui.press("playpause")
    return "Playing media."


def pause_media() -> str:
    """Pause media playback."""
    logger.info("Pressing virtual key 'playpause'")
    pyautogui.press("playpause")
    return "Paused media."


def play_pause() -> str:
    """Toggle play/pause on the active media player."""
    return play_media()


def next_track() -> str:
    """Skip to the next track."""
    logger.info("Pressing virtual key 'nexttrack'")
    pyautogui.press("nexttrack")
    return "Skipped to next track."


def previous_track() -> str:
    """Go back to the previous track."""
    logger.info("Pressing virtual key 'prevtrack'")
    pyautogui.press("prevtrack")
    return "Went to previous track."


def volume_up(steps: int = 5) -> str:
    """Increase system volume by *steps* key presses."""
    logger.info(f"Increasing volume by {steps} steps...")
    for _ in range(steps):
        pyautogui.press("volumeup")
    return "Volume increased."


def volume_down(steps: int = 5) -> str:
    """Decrease system volume by *steps* key presses."""
    logger.info(f"Decreasing volume by {steps} steps...")
    for _ in range(steps):
        pyautogui.press("volumedown")
    return "Volume decreased."


def mute() -> str:
    """Toggle system mute."""
    logger.info("Pressing virtual key 'volumemute'")
    pyautogui.press("volumemute")
    return "Mute toggled."
