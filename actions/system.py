"""
actions/system.py
=================
STUB — Phase 8

System information queries (CPU, RAM, battery) and controlled system
commands (shutdown, restart — both require confirmation). Uses psutil.
"""
from __future__ import annotations


def get_cpu_usage() -> str:
    """Return spoken CPU usage, e.g. "CPU usage is 34 percent."."""
    raise NotImplementedError("get_cpu_usage is implemented in Phase 8.")


def get_ram_usage() -> str:
    """Return spoken RAM usage, e.g. "You are using 6.2 GB of 16 GB."."""
    raise NotImplementedError("get_ram_usage is implemented in Phase 8.")


def get_battery_status() -> str:
    """Return spoken battery status, e.g. "Battery is at 72 percent, charging."."""
    raise NotImplementedError("get_battery_status is implemented in Phase 8.")


def get_system_info() -> str:
    """Return a brief system summary (OS, CPU, RAM, battery)."""
    raise NotImplementedError("get_system_info is implemented in Phase 8.")


def shutdown() -> str:
    """
    Initiate system shutdown.

    REQUIRES confirmation via security/confirmation.py before calling.
    """
    raise NotImplementedError("shutdown is implemented in Phase 8.")


def restart() -> str:
    """
    Initiate system restart.

    REQUIRES confirmation via security/confirmation.py before calling.
    """
    raise NotImplementedError("restart is implemented in Phase 8.")
