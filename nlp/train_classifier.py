"""
nlp/train_classifier.py
========================
Standalone script to train the intent classifier on data/intents.csv
and save models to models/*.pkl.
"""
import os
import sys

# Ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.settings import Settings
from nlp.intent_classifier import IntentClassifier
from utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    print("=" * 60)
    print("  ORION — Training ML Intent Classifier")
    print("=" * 60)

    classifier = IntentClassifier()
    csv_path = Settings.DATA_DIR / "intents.csv"

    try:
        metrics = classifier.train(csv_path)
        print("\n[ORION] Training completed successfully!")
        print(f"  Samples  : {metrics['num_samples']}")
        print(f"  Accuracy : {metrics['accuracy']:.2%}")
        print(f"  Saved to : {Settings.MODELS_DIR}\n")
    except Exception as e:
        print(f"\n[ORION] ERROR: Training failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
