"""
actions/screenshots.py
======================
Capture and save screenshots using pyautogui + Pillow.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
import pyautogui

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


def take_screenshot(save_dir: Path | None = None) -> str:
    """
    Capture the full screen and save it as a timestamped PNG.

    Args:
        save_dir: Directory to save the screenshot (default: screenshots/).

    Returns:
        Spoken confirmation with the save path.
    """
    target_dir = save_dir or Settings.SCREENSHOTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"orion_{timestamp}.png"
    filepath = target_dir / filename

    logger.info(f"Taking screenshot... saving to {filepath}")
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)

        # Try to copy path to clipboard if pyperclip is available
        try:
            import pyperclip
            pyperclip.copy(str(filepath.resolve()))
        except Exception:
            pass

        logger.info(f"Screenshot saved successfully at {filepath}")
        return f"Screenshot saved as {filename}."
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        return "Failed to take screenshot."
