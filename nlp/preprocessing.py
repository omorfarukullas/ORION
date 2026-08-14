"""
nlp/preprocessing.py
====================
Text preprocessing pipeline: lowercasing, tokenisation, stop-word
removal, and stemming. Runs before TF-IDF vectorisation.
"""
from __future__ import annotations
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

from utils.logger import get_logger

logger = get_logger(__name__)

# Ensure NLTK data resources are available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

_stemmer = PorterStemmer()
_stop_words = set(stopwords.words("english"))


def tokenise(text: str) -> list[str]:
    """
    Tokenise *text* into a list of lowercase word tokens.

    Args:
        text: Raw text string.

    Returns:
        List of lowercase string tokens.
    """
    if not text:
        return []
    cleaned = re.sub(r"[^\w\s]", "", text.lower()).strip()
    tokens = word_tokenize(cleaned)
    return tokens


def preprocess(text: str) -> str:
    """
    Normalise raw text for the intent classifier.

    Steps:
        1. Lowercase & strip punctuation
        2. Tokenise
        3. Remove NLTK English stop words
        4. Apply Porter stemming

    Args:
        text: Raw or wake-word-stripped command string.

    Returns:
        Space-joined preprocessed token string.
    """
    tokens = tokenise(text)
    if not tokens:
        return ""

    filtered = [t for t in tokens if t not in _stop_words]
    if not filtered:
        filtered = tokens

    stemmed = [_stemmer.stem(t) for t in filtered]
    return " ".join(stemmed)
