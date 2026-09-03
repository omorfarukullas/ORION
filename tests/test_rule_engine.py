"""
tests/test_rule_engine.py
==========================
Unit tests for nlp.rule_engine.RuleEngine.
"""
import unittest

from nlp.rule_engine import RuleEngine


class TestRuleEngine(unittest.TestCase):
    """Test suite for keyword matching and entity extraction."""

    def setUp(self):
        self.engine = RuleEngine()

    def test_time_intent(self):
        cmd = self.engine.parse("what time is it")
        self.assertEqual(cmd.intent, "TIME")
        self.assertIsNone(cmd.entity)

    def test_date_intent(self):
        cmd = self.engine.parse("what day is today")
        self.assertEqual(cmd.intent, "DATE")
        self.assertIsNone(cmd.entity)

    def test_open_app_entity_extraction(self):
        cmd = self.engine.parse("open chrome")
        self.assertEqual(cmd.intent, "OPEN_APP")
        self.assertEqual(cmd.entity, "chrome")

    def test_web_search_entity(self):
        cmd = self.engine.parse("search google for python tutorials")
        self.assertEqual(cmd.intent, "WEB_SEARCH")
        self.assertEqual(cmd.entity, "python tutorials")

    def test_youtube_entity(self):
        cmd = self.engine.parse("search youtube for lofi music")
        self.assertEqual(cmd.intent, "YOUTUBE_SEARCH")
        self.assertEqual(cmd.entity, "lofi music")

    def test_screenshot_intent(self):
        cmd = self.engine.parse("take a screenshot")
        self.assertEqual(cmd.intent, "SCREENSHOT")
        self.assertIsNone(cmd.entity)

    def test_unknown_intent(self):
        cmd = self.engine.parse("tell me a joke")
        self.assertEqual(cmd.intent, "UNKNOWN")
        self.assertIsNone(cmd.entity)


if __name__ == "__main__":
    unittest.main()
