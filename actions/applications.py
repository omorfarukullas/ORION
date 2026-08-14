"""
actions/applications.py
=======================
Open desktop applications using allow-listed paths from config/applications.json.
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
from pathlib import Path

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


def _load_app_mapping() -> dict[str, str]:
    """Load application mapping from applications.json."""
    config_path = Settings.CONFIG_DIR / "applications.json"
    if not config_path.exists():
        logger.error(f"applications.json not found at {config_path}")
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Filter out comments
            return {k.lower(): v for k, v in data.items() if not k.startswith("_")}
    except Exception as e:
        logger.error(f"Failed to load applications.json: {e}")
        return {}


def open_application(app_name: str) -> str:
    """
    Launch the application matching *app_name* from applications.json or system PATH.

    Args:
        app_name: Normalised app name, e.g. "chrome", "vscode".

    Returns:
        Spoken confirmation string, e.g. "Opening Chrome."
    """
    if not app_name:
        return "Which application would you like me to open?"

    key = app_name.lower().strip()
    mapping = _load_app_mapping()

    target_path = mapping.get(key)
    if not target_path:
        # Fallback to direct app name check via system PATH
        executable = shutil.which(key)
        if executable:
            target_path = executable
        else:
            logger.warning(f"Application '{app_name}' not found in applications.json or PATH.")
            return f"Sorry, I could not find the application '{app_name}'."

    expanded_path = os.path.expandvars(target_path)
    logger.info(f"Opening application '{app_name}' -> '{expanded_path}'")

    try:
        subprocess.Popen([expanded_path], shell=False)
        formatted_name = app_name.title()
        return f"Opening {formatted_name}."
    except Exception as e:
        logger.error(f"Failed to launch application '{app_name}' ({expanded_path}): {e}")
        return f"Failed to open {app_name}."


def close_application(app_name: str) -> str:
    """
    Gracefully terminate the running process matching *app_name*.

    Raises:
        NotImplementedError: Until Phase 8 is implemented.
    """
    raise NotImplementedError("close_application is implemented in Phase 8.")


def list_running_apps() -> list[str]:
    """Return a list of currently running application names via psutil."""
    raise NotImplementedError("list_running_apps is implemented in Phase 8.")
