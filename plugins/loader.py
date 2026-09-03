"""
plugins/loader.py
=================
Dynamic plugin loader for ORION.

Scans the local plugins directory, validates manifests, and mounts
dynamic intent handlers and keywords into the action dispatcher.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from pathlib import Path
from typing import Any

from plugins.registry import plugin_registry
from utils.logger import get_logger

logger = get_logger(__name__)


class PluginLoader:
    """Discovers and mounts plugins into ORION at runtime."""

    def __init__(self, plugins_dir: Path | None = None) -> None:
        self.plugins_dir: Path = plugins_dir or plugin_registry.plugins_dir
        self.loaded_handlers: dict[str, Callable[..., str]] = {}

    def discover_and_load(self) -> int:
        """Scan and load all valid enabled plugins."""
        loaded_count = 0
        installed = plugin_registry.list_installed_plugins()
        for meta in installed:
            if not meta.get("enabled", True):
                continue
            plugin_id = meta.get("id")
            entry_file = Path(meta["local_path"]) / meta.get("entrypoint", "main.py")
            if entry_file.exists():
                try:
                    spec = importlib.util.spec_from_file_location(f"orion_plugin_{plugin_id}", entry_file)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        if hasattr(mod, "register_handlers"):
                            handlers = mod.register_handlers()
                            if isinstance(handlers, dict):
                                self.loaded_handlers.update(handlers)
                        loaded_count += 1
                        logger.info(f"Loaded plugin module '{plugin_id}'.")
                except Exception as e:
                    logger.error(f"Failed to load plugin module '{plugin_id}': {e}")

        return loaded_count

    def execute_handler(self, intent: str, **kwargs: Any) -> str | None:
        """Execute a loaded plugin handler if one matches the intent."""
        if intent in self.loaded_handlers:
            try:
                return self.loaded_handlers[intent](**kwargs)
            except Exception as e:
                logger.error(f"Plugin execution error for intent '{intent}': {e}")
                return f"Plugin error executing {intent}."
        return None


plugin_loader = PluginLoader()
