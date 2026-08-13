"""
nlp/preprocessing.py
=====================
STUB — Phase 6

Text preprocessing pipeline: lowercasing, tokenisation, stop-word
removal, and stemming. Runs before TF-IDF vectorisation.
"""
from __future__ import annotations
from typing import List


def preprocess(text: str) -> str:
    """
    Normalise raw text for the intent classifier.

    Steps (Phase 6):
        1. Lowercase
        2. Strip punctuation
        3. Tokenise
        4. Remove NLTK English stop words
        5. Apply Porter stemming

    Args:
        text: Raw or wake-word-stripped command string.

    Returns:
        Space-joined preprocessed token string.

    Raises:
        NotImplementedError: Until Phase 6 is implemented.
    """
    raise NotImplementedError("preprocessing is implemented in Phase 6.")


def tokenise(text: str) -> List[str]:
    """Tokenise *text* into a list of lowercase word tokens."""
    raise NotImplementedError("tokenise is implemented in Phase 6.")
