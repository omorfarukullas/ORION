"""
actions/system.py
=================
System information queries (CPU, RAM, battery) using psutil.
Controlled commands (shutdown, restart) are gated in Phase 9.
"""
from __future__ import annotations
import psutil

from utils.logger import get_logger

logger = get_logger(__name__)


def get_cpu_usage() -> str:
    """Return spoken CPU usage, e.g. "CPU usage is 34 percent."."""
    usage = psutil.cpu_percent(interval=0.1)
    msg = f"CPU usage is {usage:.0f} percent."
    logger.info(msg)
    return msg


def get_ram_usage() -> str:
    """Return spoken RAM usage, e.g. "You are using 6.2 GB of 16 GB RAM."."""
    mem = psutil.virtual_memory()
    used_gb = mem.used / (1024**3)
    total_gb = mem.total / (1024**3)
    msg = f"You are using {used_gb:.1f} GB of {total_gb:.1f} GB RAM."
    logger.info(msg)
    return msg


def get_battery_status() -> str:
    """Return spoken battery status, e.g. "Battery is at 72 percent, charging."."""
    battery = psutil.sensors_battery()
    if battery is None:
        msg = "Battery status is not available on this device."
        logger.info(msg)
        return msg

    percent = int(battery.percent)
    state = "charging" if battery.power_plugged else "discharging"
    msg = f"Battery is at {percent} percent, {state}."
    logger.info(msg)
    return msg


def get_system_info() -> str:
    """Return a brief system summary (CPU, RAM, battery)."""
    cpu = get_cpu_usage()
    ram = get_ram_usage()
    battery = get_battery_status()
    msg = f"{cpu} {ram} {battery}"
    return msg


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
