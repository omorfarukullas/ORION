"""
plugins/registry.py
===================
Cloud-connected plugin registry client for ORION.

Allows discovering, fetching, installing, and managing plugins from
a GitHub-hosted repository index or local directory.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class PluginRegistry:
    """Manages cloud catalog and locally installed ORION plugins."""

    OFFICIAL_FALLBACK_INDEX = [
        {
            "id": "spotify_controller",
            "name": "Spotify Player & Queue Controller",
            "version": "1.1.0",
            "description": "Voice controls for Spotify playback, playlists, and device volume.",
            "author": "ORION Community",
            "category": "Media",
            "intents": ["SPOTIFY_PLAY", "SPOTIFY_PAUSE", "SPOTIFY_NEXT", "SPOTIFY_PLAYLIST"],
            "url": "https://github.com/omorfarukullas/ORION-plugins/tree/main/spotify_controller",
        },
        {
            "id": "home_assistant",
            "name": "Home Assistant IoT Hub Bridge",
            "version": "1.0.2",
            "description": "Control smart lights, switches, and scenes via local Home Assistant REST/WS API.",
            "author": "ORION Core Team",
            "category": "Smart Home",
            "intents": ["LIGHTS_ON", "LIGHTS_OFF", "SCENE_ACTIVATE", "CLIMATE_SET"],
            "url": "https://github.com/omorfarukullas/ORION-plugins/tree/main/home_assistant",
        },
        {
            "id": "quick_notes",
            "name": "Quick Notes & Reminders",
            "version": "1.0.0",
            "description": "Dictate quick sticky notes, todo lists, and timed desktop alerts.",
            "author": "ORION Community",
            "category": "Productivity",
            "intents": ["CREATE_NOTE", "READ_NOTES", "SET_REMINDER"],
            "url": "https://github.com/omorfarukullas/ORION-plugins/tree/main/quick_notes",
        },
    ]

    def __init__(self, plugins_dir: Path | None = None, registry_url: str | None = None) -> None:
        self.plugins_dir: Path = plugins_dir or (Settings.ROOT_DIR / "plugins")
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.registry_url: str = registry_url or Settings.PLUGIN_REGISTRY_URL

    def fetch_cloud_catalog(self, timeout: float = 3.0) -> list[dict[str, Any]]:
        """
        Fetch available plugins from the remote GitHub registry index.
        Falls back smoothly to bundled verified index if offline or unreachable.
        """
        try:
            req = urllib.request.Request(
                self.registry_url,
                headers={"User-Agent": f"ORION-Client/{Settings.VERSION}"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    if isinstance(data, list):
                        logger.info(f"Retrieved {len(data)} plugins from GitHub registry.")
                        return data
        except Exception as e:
            logger.debug(f"Could not reach remote GitHub plugin registry ({e}). Using offline catalog.")

        return list(self.OFFICIAL_FALLBACK_INDEX)

    def list_installed_plugins(self) -> list[dict[str, Any]]:
        """List all plugins currently installed in the local plugins directory."""
        installed = []
        for item in self.plugins_dir.iterdir():
            if item.is_dir():
                manifest_path = item / "plugin.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                            meta["installed"] = True
                            meta["local_path"] = str(item)
                            installed.append(meta)
                    except Exception as err:
                        logger.warning(f"Error reading plugin manifest {manifest_path}: {err}")
        return installed

    def install_plugin(self, plugin_id: str, manifest: dict[str, Any] | None = None) -> bool:
        """Install a plugin into the local plugins directory."""
        target_dir = self.plugins_dir / plugin_id
        target_dir.mkdir(parents=True, exist_ok=True)

        meta = manifest or {
            "id": plugin_id,
            "name": plugin_id.replace("_", " ").title(),
            "version": "1.0.0",
            "description": f"Installed plugin {plugin_id}",
            "author": "Community",
            "enabled": True,
        }
        meta["enabled"] = True

        manifest_path = target_dir / "plugin.json"
        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
            logger.info(f"Plugin '{plugin_id}' installed successfully at {target_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to install plugin '{plugin_id}': {e}")
            return False

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin from the local directory."""
        target_dir = self.plugins_dir / plugin_id
        if not target_dir.exists():
            return False
        try:
            import shutil
            shutil.rmtree(target_dir)
            logger.info(f"Plugin '{plugin_id}' uninstalled.")
            return True
        except Exception as e:
            logger.error(f"Failed to uninstall plugin '{plugin_id}': {e}")
            return False


plugin_registry = PluginRegistry()
