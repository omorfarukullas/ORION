"""
tests/test_vector_classifier.py
================================
Unit tests for Vector DB intent classifier and fallback.
"""
from nlp.command_parser import CommandParser
from nlp.vector_classifier import VectorIntentClassifier


def test_vector_classifier_predict():
    clf = VectorIntentClassifier()
    clf.load()

    intent, conf = clf.predict("open notepad")
    assert intent in ("OPEN_APP", "UNKNOWN")
    assert 0.0 <= conf <= 1.0


def test_command_parser_with_vector():
    parser = CommandParser()
    parsed = parser.parse("shutdown the pc")
    assert parsed.intent == "SHUTDOWN"
    assert parsed.confidence == 1.0
