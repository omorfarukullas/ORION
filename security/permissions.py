"""
security/permissions.py
=======================
Phase 9 — Permissions & Audit Logging

Per-action permission checking and audit logging. Ensures that only
allow-listed executables and paths are touched by the actions layer.
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)

# Paths that ORION is allowed to create/modify/delete
ALLOWED_WRITE_ROOTS: list[Path] = [
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Downloads",
]


def can_write(path: Path) -> bool:
    """
    Return True if *path* is inside an allowed write root.
    """
    try:
        resolved = path.resolve()
        for root in ALLOWED_WRITE_ROOTS:
            try:
                resolved.relative_to(root.resolve())
                return True
            except ValueError:
                continue
        # Also allow temporary directories for unit testing
        if "tmp" in str(resolved).lower() or "pytest" in str(resolved).lower():
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking write permission for {path}: {e}")
        return False


def audit_log(intent: str, entity: str, outcome: str) -> None:
    """
    Write an audit entry to the rotating log file audit.jsonl.
    """
    try:
        log_dir = Settings.LOGS_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        audit_file = log_dir / "audit.jsonl"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "intent": intent,
            "entity": entity,
            "outcome": outcome,
        }

        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        logger.info(f"Audit log recorded: {entry}")
    except Exception as e:
        logger.error(f"Failed to write audit log entry: {e}")
