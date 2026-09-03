"""
tests/test_personas.py
======================
Unit tests for speech personas and voice profile management.
"""

import unittest

from speech.personas import PersonaManager


class TestPersonas(unittest.TestCase):
    """Test suite for voice personas."""

    def setUp(self) -> None:
        self.manager = PersonaManager(default_persona="professional")

    def test_default_persona_is_professional(self):
        self.assertEqual(self.manager.active_persona.id, "professional")
        self.assertEqual(self.manager.active_persona.rate, 175)

    def test_switch_to_friendly_persona(self):
        success = self.manager.set_persona("friendly")
        self.assertTrue(success)
        self.assertEqual(self.manager.active_persona.id, "friendly")
        self.assertEqual(self.manager.active_persona.rate, 190)

    def test_friendly_persona_text_transform(self):
        self.manager.set_persona("friendly")
        res = self.manager.active_persona.transform_text("Calculated: 100")
        self.assertTrue(res.startswith("Sure thing!"))

    def test_switch_by_display_name(self):
        success = self.manager.set_persona("Friendly Mode")
        self.assertTrue(success)
        self.assertEqual(self.manager.active_persona.id, "friendly")

    def test_switch_invalid_persona_fallback(self):
        success = self.manager.set_persona("non_existent_persona")
        self.assertFalse(success)
        # Should keep current
        self.assertEqual(self.manager.active_persona.id, "professional")

    def test_list_personas_returns_all(self):
        personas = self.manager.list_personas()
        self.assertGreaterEqual(len(personas), 3)
        ids = [p["id"] for p in personas]
        self.assertIn("professional", ids)
        self.assertIn("friendly", ids)
        self.assertIn("coqui_clone", ids)

    def test_register_custom_clone(self):
        self.manager.register_custom_clone("My Voice Clone", "/path/to/model.pth", rate=165)
        personas = self.manager.list_personas()
        names = [p["name"] for p in personas]
        self.assertIn("My Voice Clone", names)


if __name__ == "__main__":
    unittest.main()
