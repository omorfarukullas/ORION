"""
utils/logger.py
===============
Centralised logging factory for ORION.

Usage::

    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Something happened")

All loggers share a single root "orion" logger that writes to both the
console (colour-coded via colorlog) and a rotating file in logs/.
"""

import logging
import logging.handlers
import os
from pathlib import Path


def _build_root_logger() -> logging.Logger:
    """
    Build and configure the root ORION logger on first call.
    Subsequent calls return the already-configured logger.
    """
    root = logging.getLogger("orion")

    if root.handlers:
        # Already configured — don't add duplicate handlers
        return root

    root.setLevel(logging.DEBUG)

    # ── Console handler (coloured if colorlog is available) ───────────────────
    try:
        import colorlog  # type: ignore
        console_fmt = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)-8s]%(reset)s "
            "%(cyan)s%(name)s%(reset)s — %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG":    "white",
                "INFO":     "green",
                "WARNING":  "yellow",
                "ERROR":    "red",
                "CRITICAL": "bold_red",
            },
        )
    except ImportError:
        console_fmt = logging.Formatter(  # type: ignore[assignment]
            "%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
            datefmt="%H:%M:%S",
        )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_fmt)
    root.addHandler(console_handler)

    # ── File handler (rotating, 5 MB × 3 backups) ─────────────────────────────
    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "orion.log"

    file_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_fmt)
    root.addHandler(file_handler)

    return root


def get_logger(name: str) -> logging.Logger:
    """
    Return a child logger of the ORION root logger.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    _build_root_logger()
    # Strip the project prefix to keep log names tidy
    short = name.replace("orion.", "")
    return logging.getLogger(f"orion.{short}")
