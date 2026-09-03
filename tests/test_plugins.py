"""
tests/test_plugins.py
=====================
Unit tests for cloud plugin registry and dynamic plugin loading.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from plugins.registry import PluginRegistry
from plugins.loader import PluginLoader


class TestPlugins(unittest.TestCase):
    """Test suite for plugin registry and loader."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.registry = PluginRegistry(plugins_dir=self.temp_dir)
        self.loader = PluginLoader(plugins_dir=self.temp_dir)

    def tearDown(self) -> None:
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_fetch_cloud_catalog_fallback(self):
        catalog = self.registry.fetch_cloud_catalog()
        self.assertIsInstance(catalog, list)
        self.assertGreaterEqual(len(catalog), 1)
        ids = [p["id"] for p in catalog]
        self.assertIn("spotify_controller", ids)

    def test_install_and_list_plugin(self):
        success = self.registry.install_plugin("test_plugin", manifest={
            "id": "test_plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A unit test plugin",
        })
        self.assertTrue(success)

        installed = self.registry.list_installed_plugins()
        self.assertEqual(len(installed), 1)
        self.assertEqual(installed[0]["id"], "test_plugin")

    def test_uninstall_plugin(self):
        self.registry.install_plugin("dummy_plugin")
        self.assertTrue((self.temp_dir / "dummy_plugin").exists())

        res = self.registry.uninstall_plugin("dummy_plugin")
        self.assertTrue(res)
        self.assertFalse((self.temp_dir / "dummy_plugin").exists())

    def test_uninstall_nonexistent_plugin(self):
        res = self.registry.uninstall_plugin("ghost_plugin")
        self.assertFalse(res)


if __name__ == "__main__":
    unittest.main()
