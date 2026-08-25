"""
actions/files.py
================
File system operations: create, find, rename, and delete files/folders.
Destructive operations (delete_file) will be gated by security/command_validator.py in Phase 9.
"""
from __future__ import annotations
import os
import shutil
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


def _get_default_parent() -> Path:
    """Return default parent directory (Desktop or User Home)."""
    desktop = Path.home() / "Desktop"
    if desktop.exists():
        return desktop
    return Path.home()


def create_folder(name: str, parent: Path | None = None) -> str:
    """Create a directory named *name* inside *parent* (default: Desktop)."""
    if not name:
        return "Please specify a folder name."

    target_parent = parent or _get_default_parent()
    folder_path = target_parent / name

    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created folder: {folder_path}")
        return f"Created folder {name}."
    except Exception as e:
        logger.error(f"Failed to create folder '{name}': {e}")
        return f"Failed to create folder {name}."


def create_file(name: str, parent: Path | None = None) -> str:
    """Create an empty file named *name* inside *parent* (default: Desktop)."""
    if not name:
        return "Please specify a file name."

    target_parent = parent or _get_default_parent()
    file_path = target_parent / name

    try:
        target_parent.mkdir(parents=True, exist_ok=True)
        file_path.touch(exist_ok=True)
        logger.info(f"Created file: {file_path}")
        return f"Created file {name}."
    except Exception as e:
        logger.error(f"Failed to create file '{name}': {e}")
        return f"Failed to create file {name}."


def find_file(name: str, search_root: Path | None = None, max_depth: int = 3) -> str:
    """
    Search for *name* recursively from *search_root* (default: Desktop/Documents).
    Limits search depth to *max_depth* to keep search fast and local.
    """
    if not name:
        return "Please specify a file name to search for."

    roots = [search_root] if search_root else [_get_default_parent(), Path.home() / "Documents", Path.home() / "Downloads"]
    logger.info(f"Searching for file '{name}' under search roots...")

    matches = []
    target_lower = name.lower()

    for root in roots:
        if not root.exists():
            continue
        try:
            for root_dir, dirs, files in os.walk(root):
                # Calculate current depth relative to root
                rel_path = Path(root_dir).relative_to(root)
                if len(rel_path.parts) > max_depth:
                    dirs.clear()  # Don't recurse deeper
                    continue

                for file in files:
                    if file.lower() == target_lower or target_lower in file.lower():
                        matches.append(Path(root_dir) / file)
                        if len(matches) >= 3:
                            break
                if len(matches) >= 3:
                    break
        except Exception as e:
            logger.error(f"Error searching in '{root}': {e}")

        if matches:
            break

    if matches:
        first_match = matches[0]
        logger.info(f"Found file '{name}' at: {first_match}")
        return f"Found {name} at {first_match}."
    else:
        logger.info(f"File '{name}' not found.")
        return f"Could not find any file named {name}."


def rename_file(old_name: str, new_name: str, parent: Path | None = None) -> str:
    """Rename *old_name* to *new_name* in *parent*."""
    if not old_name or not new_name:
        return "Please specify both the original name and the new name."

    target_parent = parent or _get_default_parent()
    old_path = target_parent / old_name
    new_path = target_parent / new_name

    if not old_path.exists():
        logger.warning(f"Cannot rename: '{old_path}' does not exist.")
        return f"Could not find {old_name} to rename."

    try:
        old_path.rename(new_path)
        logger.info(f"Renamed '{old_path}' to '{new_path}'")
        return f"Renamed {old_name} to {new_name}."
    except Exception as e:
        logger.error(f"Failed to rename '{old_name}' to '{new_name}': {e}")
        return f"Failed to rename {old_name}."


def delete_file(name: str, parent: Path | None = None) -> str:
    """
    Delete *name* in *parent*.
    REQUIRES confirmation via security/confirmation.py before calling.
    """
    if not name:
        return "Please specify a file or folder name to delete."

    target_parent = parent or _get_default_parent()
    target_path = target_parent / name

    if not target_path.exists():
        logger.warning(f"Cannot delete: '{target_path}' does not exist.")
        return f"Could not find {name} to delete."

    try:
        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        logger.info(f"Deleted: {target_path}")
        return f"Deleted {name}."
    except Exception as e:
        logger.error(f"Failed to delete '{name}': {e}")
        return f"Failed to delete {name}."
