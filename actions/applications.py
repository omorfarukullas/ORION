"""
actions/applications.py
=======================
Open desktop applications using allow-listed paths from config/applications.json
and Windows Registry / PATH lookups.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

import psutil

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


def _find_in_registry(app_name: str) -> str | None:
    """Check Windows App Paths registry key for application executable."""
    if sys.platform != "win32":
        return None

    try:
        import winreg
        key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{app_name}.exe"
        for hkey in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                with winreg.OpenKey(hkey, key_path) as key:
                    val, _ = winreg.QueryValueEx(key, "")
                    if val and os.path.exists(val):
                        return val
            except FileNotFoundError:
                continue
    except Exception as e:
        logger.debug(f"Registry lookup error for {app_name}: {e}")
    return None


def open_application(app_name: str) -> str:
    """
    Launch the application matching *app_name* from applications.json, registry, or system PATH.

    Args:
        app_name: Normalised app name, e.g. "chrome", "vscode", "notepad".

    Returns:
        Spoken confirmation string, e.g. "Opening Chrome."
    """
    if not app_name:
        return "Which application would you like me to open?"

    key = app_name.lower().strip()
    # Strip common redundant suffixes
    clean_key = re.sub(r"\s+(browser|tab|app|application)$", "", key).strip()

    mapping = _load_app_mapping()

    target_path = mapping.get(key) or mapping.get(clean_key)

    if target_path and target_path.startswith(("http://", "https://")):
        import webbrowser
        logger.info(f"Opening web target for '{app_name}' -> '{target_path}'")
        webbrowser.open(target_path)
        return f"Opening {app_name.title()}."

    if not target_path:
        # Fallback 1: Direct app name check via system PATH
        executable = shutil.which(key) or shutil.which(clean_key)
        if executable:
            target_path = executable

    if not target_path:
        # Fallback 2: Check Windows Registry App Paths
        registry_path = _find_in_registry(key) or _find_in_registry(clean_key)
        if registry_path:
            target_path = registry_path

    if not target_path:
        logger.warning(f"Application '{app_name}' not found in applications.json, PATH, or Registry.")
        return f"Sorry, I could not find the application '{app_name}'."

    expanded_path = os.path.expandvars(target_path)
    logger.info(f"Opening application '{app_name}' -> '{expanded_path}'")

    try:
        import shlex
        if expanded_path.startswith(("ms-", "http://", "https://")):
            os.startfile(expanded_path)
        else:
            cmd_args = shlex.split(expanded_path, posix=False)
            subprocess.Popen(cmd_args, shell=False)
        formatted_name = app_name.title()
        return f"Opening {formatted_name}."
    except Exception as e:
        logger.error(f"Failed to launch application '{app_name}' ({expanded_path}): {e}")
        return f"Failed to open {app_name}."


def close_application(app_name: str) -> str:
    """
    Gracefully terminate the running process matching *app_name*.
    """
    if not app_name:
        return "Which application would you like me to close?"

    target = app_name.lower().strip()
    terminated_count = 0

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info['name']
            if pname and target in pname.lower():
                proc.terminate()
                terminated_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if terminated_count > 0:
        logger.info(f"Closed {terminated_count} process(es) matching '{app_name}'.")
        return f"Closed {app_name.title()}."
    else:
        logger.warning(f"No running process found matching '{app_name}'.")
        return f"Could not find a running application named {app_name}."


def list_running_apps() -> list[str]:
    """Return a list of currently running application names via psutil."""
    apps = set()
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name:
                apps.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(apps)
