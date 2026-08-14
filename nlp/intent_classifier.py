"""
nlp/intent_classifier.py
=========================
TF-IDF + Logistic Regression intent classifier.
Trained on data/intents.csv, serialised to models/*.pkl.
"""
from __future__ import annotations
from pathlib import Path
from typing import Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from config.settings import Settings
from nlp.preprocessing import preprocess
from utils.logger import get_logger

logger = get_logger(__name__)


class IntentClassifier:
    """
    Classifies a preprocessed command string into one of the ORION intents.

    Confidence thresholds (Operating Rule 5):
        - > 80 % → execute immediately
        - 50–80 % → ask for confirmation
        - < 50 % → ask for clarification
    """

    def __init__(
        self,
        vectoriser_path: Path = Settings.MODELS_DIR / "tfidf_vectorizer.pkl",
        model_path: Path = Settings.MODELS_DIR / "intent_classifier.pkl",
    ) -> None:
        self.vectoriser_path = vectoriser_path
        self.model_path = model_path
        self._vectoriser: TfidfVectorizer | None = None
        self._model: LogisticRegression | None = None

    def load(self) -> None:
        """Load pre-trained model files from disk."""
        if not self.vectoriser_path.exists() or not self.model_path.exists():
            raise FileNotFoundError(
                f"Model files not found. Expected {self.vectoriser_path} and {self.model_path}."
            )

        logger.info(f"Loading intent classifier models from {Settings.MODELS_DIR}...")
        self._vectoriser = joblib.load(self.vectoriser_path)
        self._model = joblib.load(self.model_path)
        logger.info("Intent classifier models loaded successfully.")

    def train(self, csv_path: Path | str = Settings.DATA_DIR / "intents.csv") -> dict[str, float]:
        """
        Train and save the classifier from intents.csv.

        Returns:
            Dictionary containing training performance metrics (accuracy).
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"Training dataset not found at {csv_file}")

        logger.info(f"Training intent classifier on dataset {csv_file}...")
        df = pd.read_csv(csv_file)

        df["clean_text"] = df["text"].astype(str).apply(preprocess)
        X_text = df["clean_text"]
        y = df["intent"]

        self._vectoriser = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        X_vec = self._vectoriser.fit_transform(X_text)

        self._model = LogisticRegression(max_iter=500, C=5.0, solver="lbfgs")
        self._model.fit(X_vec, y)

        accuracy = float(self._model.score(X_vec, y))
        logger.info(f"Training complete. Training Accuracy: {accuracy:.2%}")

        Settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._vectoriser, self.vectoriser_path)
        joblib.dump(self._model, self.model_path)
        logger.info(f"Models saved to {self.vectoriser_path} and {self.model_path}")

        return {"accuracy": accuracy, "num_samples": len(df)}

    def predict(self, text: str) -> Tuple[str, float]:
        """
        Predict intent and confidence for *text*.

        Returns:
            (intent_label, confidence) e.g. ("OPEN_APP", 0.93)
        """
        if self._vectoriser is None or self._model is None:
            self.load()

        processed_text = preprocess(text)
        if not processed_text:
            return ("UNKNOWN", 0.0)

        vec = self._vectoriser.transform([processed_text])
        probabilities = self._model.predict_proba(vec)[0]
        max_idx = int(np.argmax(probabilities))

        intent_label = str(self._model.classes_[max_idx])
        confidence = float(probabilities[max_idx])

        logger.info(f"Predicted intent '{intent_label}' with confidence {confidence:.2%} for input '{text}'")
        return (intent_label, confidence)
