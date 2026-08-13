"""
actions/screenshots.py
======================
STUB — Phase 8

Capture and save screenshots using pyautogui + Pillow.
"""
from __future__ import annotations
from pathlib import Path


def take_screenshot(save_dir: Path | None = None) -> str:
    """
    Capture the full screen and save it as a timestamped PNG.

    Args:
        save_dir: Directory to save the screenshot (default: screenshots/).

    Returns:
        Spoken confirmation with the save path.

    Raises:
        NotImplementedError: Until Phase 8 is implemented.
    """
    raise NotImplementedError("take_screenshot is implemented in Phase 8.")
