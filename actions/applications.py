"""
actions/applications.py
=======================
STUB — Phase 8

Open and close desktop applications using subprocess (allow-listed paths
from config/applications.json) and psutil for process management.
"""
from __future__ import annotations


def open_application(app_name: str) -> str:
    """
    Launch the application matching *app_name* from applications.json.

    Args:
        app_name: Normalised app name, e.g. "chrome", "vscode".

    Returns:
        Spoken confirmation string, e.g. "Opening Chrome."

    Raises:
        NotImplementedError: Until Phase 8 is implemented.
    """
    raise NotImplementedError("open_application is implemented in Phase 8.")


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
