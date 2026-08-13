"""
security/permissions.py
=======================
STUB — Phase 9

Per-action permission checking and audit logging. Ensures that only
allow-listed executables and paths are touched by the actions layer.
"""
from __future__ import annotations
from pathlib import Path


# Paths that ORION is allowed to create/modify/delete
# All other paths require an explicit user override (Phase 9)
ALLOWED_WRITE_ROOTS: list[Path] = [
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Downloads",
]


def can_write(path: Path) -> bool:
    """
    Return True if *path* is inside an allowed write root.

    Raises:
        NotImplementedError: Until Phase 9 is implemented.
    """
    raise NotImplementedError("can_write is implemented in Phase 9.")


def audit_log(intent: str, entity: str, outcome: str) -> None:
    """
    Write an audit entry to the rotating log file.

    Raises:
        NotImplementedError: Until Phase 9 is implemented.
    """
    raise NotImplementedError("audit_log is implemented in Phase 9.")
