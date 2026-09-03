"""
tests/test_web_api.py
=====================
Unit tests for ORION FastAPI endpoints and WebSocket API.
"""

import unittest

from fastapi.testclient import TestClient

from api.server import create_app


class TestWebApi(unittest.TestCase):
    """Test suite for FastAPI REST and WebSocket endpoints."""

    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_get_status_endpoint(self):
        res = self.client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("name", data)
        self.assertIn("status", data)
        self.assertIn("persona", data)
        self.assertIn("cpu_percent", data)

    def test_get_metrics_endpoint(self):
        res = self.client.get("/api/metrics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("cpu_percent", data)
        self.assertIn("ram_percent", data)

    def test_get_personas_endpoint(self):
        res = self.client.get("/api/personas")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("active", data)
        self.assertIn("personas", data)

    def test_select_persona_endpoint(self):
        res = self.client.post("/api/personas/select", json={"persona_id": "friendly"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

    def test_select_invalid_persona_returns_404(self):
        res = self.client.post("/api/personas/select", json={"persona_id": "invalid_one"})
        self.assertEqual(res.status_code, 404)

    def test_post_command_endpoint(self):
        res = self.client.post("/api/command", json={"command": "what time is it"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["raw_text"], "what time is it")
        self.assertEqual(data["intent"], "TIME")
        self.assertTrue(data["success"])

    def test_post_empty_command_returns_400(self):
        res = self.client.post("/api/command", json={"command": "   "})
        self.assertEqual(res.status_code, 400)

    def test_get_history_endpoint(self):
        res = self.client.get("/api/history")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("history", data)

    def test_list_plugins_endpoint(self):
        res = self.client.get("/api/plugins")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("installed", data)
        self.assertIn("catalog", data)


if __name__ == "__main__":
    unittest.main()
