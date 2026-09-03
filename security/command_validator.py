"""
security/command_validator.py
==============================
Phase 9 & 11 — Command Validator

Allow-list gate: classifies an intent into SAFE / DESTRUCTIVE / FORBIDDEN
before the actions layer executes anything.
"""
from __future__ import annotations

from enum import Enum, auto


class RiskLevel(Enum):
    SAFE        = auto()   # Execute immediately
    DESTRUCTIVE = auto()   # Require spoken confirmation first
    FORBIDDEN   = auto()   # Do not implement — refuse politely


# Intent risk classification table
INTENT_RISK: dict[str, RiskLevel] = {
    # Safe
    "OPEN_APP":       RiskLevel.SAFE,
    "CLOSE_APP":      RiskLevel.SAFE,
    "OPEN_WEBSITE":   RiskLevel.SAFE,
    "WEB_SEARCH":     RiskLevel.SAFE,
    "YOUTUBE_SEARCH": RiskLevel.SAFE,
    "SYSTEM_CPU":     RiskLevel.SAFE,
    "SYSTEM_RAM":     RiskLevel.SAFE,
    "SYSTEM_BATTERY": RiskLevel.SAFE,
    "SYSTEM_INFO":    RiskLevel.SAFE,
    "CREATE_FOLDER":  RiskLevel.SAFE,
    "CREATE_FILE":    RiskLevel.SAFE,
    "FIND_FILE":      RiskLevel.SAFE,
    "RENAME_FILE":    RiskLevel.SAFE,
    "PLAY_MEDIA":     RiskLevel.SAFE,
    "PAUSE_MEDIA":    RiskLevel.SAFE,
    "NEXT_TRACK":     RiskLevel.SAFE,
    "PREVIOUS_TRACK": RiskLevel.SAFE,
    "VOLUME_UP":      RiskLevel.SAFE,
    "VOLUME_DOWN":    RiskLevel.SAFE,
    "MUTE":           RiskLevel.SAFE,
    "TIME":           RiskLevel.SAFE,
    "DATE":           RiskLevel.SAFE,
    "SCREENSHOT":     RiskLevel.SAFE,
    "REMEMBER":       RiskLevel.SAFE,
    "RECALL":         RiskLevel.SAFE,
    "WEATHER":        RiskLevel.SAFE,
    "CALCULATE":      RiskLevel.SAFE,
    "CLIPBOARD_READ": RiskLevel.SAFE,
    "CLIPBOARD_COPY": RiskLevel.SAFE,
    "CLIPBOARD_CLEAR":RiskLevel.SAFE,
    "ASK_ORION":      RiskLevel.SAFE,
    # Destructive — require confirmation
    "DELETE_FILE":    RiskLevel.DESTRUCTIVE,
    "SHUTDOWN":       RiskLevel.DESTRUCTIVE,
    "RESTART":        RiskLevel.DESTRUCTIVE,
}


def get_risk_level(intent: str) -> RiskLevel:
    """
    Return the risk level for *intent*. Unknown intents default to FORBIDDEN.
    """
    return INTENT_RISK.get(intent, RiskLevel.FORBIDDEN)


def is_safe(intent: str) -> bool:
    """Return True if intent can execute immediately."""
    return get_risk_level(intent) == RiskLevel.SAFE


def is_destructive(intent: str) -> bool:
    """Return True if intent requires spoken confirmation."""
    return get_risk_level(intent) == RiskLevel.DESTRUCTIVE
