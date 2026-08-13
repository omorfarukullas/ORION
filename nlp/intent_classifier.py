"""
nlp/intent_classifier.py
=========================
STUB — Phase 6

TF-IDF + Logistic Regression intent classifier.
Trained on data/intents.csv, serialised to models/*.pkl.
"""
from __future__ import annotations
from typing import Tuple


class IntentClassifier:
    """
    Classifies a preprocessed command string into one of the 20+ ORION intents.

    Architecture (Phase 6):
        - TF-IDF vectoriser (sklearn TfidfVectorizer)
        - Logistic Regression classifier (sklearn LogisticRegression)
        - Serialised via joblib to models/tfidf_vectorizer.pkl and
          models/intent_classifier.pkl

    Confidence thresholds (Operating Rule 5):
        - > 80 % → execute immediately
        - 50–80 % → ask for confirmation
        - < 50 % → ask for clarification
    """

    def __init__(self) -> None:
        self._vectoriser = None
        self._model = None

    def load(self) -> None:
        """Load pre-trained model files from models/."""
        raise NotImplementedError("IntentClassifier is implemented in Phase 6.")

    def train(self, csv_path: str) -> None:
        """Train and save the classifier from intents.csv."""
        raise NotImplementedError("IntentClassifier is implemented in Phase 6.")

    def predict(self, text: str) -> Tuple[str, float]:
        """
        Predict intent and confidence for *text*.

        Returns:
            (intent_label, confidence) e.g. ("OPEN_APP", 0.93)
        """
        raise NotImplementedError("IntentClassifier is implemented in Phase 6.")
