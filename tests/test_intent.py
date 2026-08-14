"""
tests/test_intent.py
====================
Unit tests for preprocessing, training, and predicting with IntentClassifier.
"""
import unittest
from pathlib import Path
from nlp.preprocessing import preprocess, tokenise
from nlp.intent_classifier import IntentClassifier
from nlp.command_dispatcher import dispatch_with_confidence


class TestPreprocessing(unittest.TestCase):
    """Test suite for nlp.preprocessing."""

    def test_preprocess_lowercase_and_punctuation(self):
        text = "Hello, WORLD! What is the time?"
        result = preprocess(text)
        self.assertEqual(result, "hello world time")

    def test_tokenise_returns_list(self):
        tokens = tokenise("Open Chrome please!")
        self.assertEqual(tokens, ["open", "chrome", "please"])

    def test_empty_string_handling(self):
        self.assertEqual(preprocess(""), "")
        self.assertEqual(tokenise(""), [])


class TestIntentClassifier(unittest.TestCase):
    """Test suite for nlp.intent_classifier.IntentClassifier."""

    def setUp(self):
        self.classifier = IntentClassifier()

    def test_predict_trained_model(self):
        intent, conf = self.classifier.predict("what time is it")
        self.assertEqual(intent, "TIME")
        self.assertGreater(conf, 0.5)

    def test_predict_open_app(self):
        intent, conf = self.classifier.predict("open visual studio code")
        self.assertEqual(intent, "OPEN_APP")
        self.assertGreater(conf, 0.5)

    def test_predict_returns_tuple(self):
        result = self.classifier.predict("take a screenshot")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], float)

    def test_load_raises_when_files_missing(self):
        fake_classifier = IntentClassifier(
            vectoriser_path=Path("nonexistent_vec.pkl"),
            model_path=Path("nonexistent_model.pkl"),
        )
        with self.assertRaises(FileNotFoundError):
            fake_classifier.load()


class TestConfidenceGating(unittest.TestCase):
    """Test suite for Operating Rule 5 confidence threshold gating."""

    def test_high_confidence_executes(self):
        res = dispatch_with_confidence("TIME", 0.95, None, "what time is it")
        self.assertTrue(res.startswith("The time is"))

    def test_medium_confidence_asks_confirmation(self):
        res = dispatch_with_confidence("TIME", 0.65, None, "time?")
        self.assertTrue(res.startswith("I think you meant time."))

    def test_low_confidence_clarifies(self):
        res = dispatch_with_confidence("TIME", 0.30, None, "huh")
        self.assertTrue("not confident" in res)


if __name__ == "__main__":
    unittest.main()
