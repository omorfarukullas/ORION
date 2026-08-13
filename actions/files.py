"""
actions/files.py
================
STUB — Phase 8

File system operations: create, find, rename, and delete files/folders.
All destructive operations go through security/command_validator.py first.
"""
from __future__ import annotations
from pathlib import Path


def create_folder(name: str, parent: Path | None = None) -> str:
    """Create a directory named *name* inside *parent* (default: Desktop)."""
    raise NotImplementedError("create_folder is implemented in Phase 8.")


def create_file(name: str, parent: Path | None = None) -> str:
    """Create an empty file named *name* inside *parent* (default: Desktop)."""
    raise NotImplementedError("create_file is implemented in Phase 8.")


def find_file(name: str, search_root: Path | None = None) -> str:
    """Search for *name* recursively from *search_root* (default: home dir)."""
    raise NotImplementedError("find_file is implemented in Phase 8.")


def rename_file(old_name: str, new_name: str, parent: Path | None = None) -> str:
    """Rename *old_name* to *new_name* in *parent*."""
    raise NotImplementedError("rename_file is implemented in Phase 8.")


def delete_file(name: str, parent: Path | None = None) -> str:
    """
    Delete *name* in *parent*.

    REQUIRES confirmation via security/confirmation.py before calling.
    """
    raise NotImplementedError("delete_file is implemented in Phase 8.")
