"""
nlp/vector_classifier.py
========================
Vector Database Intent Classifier using ChromaDB + SentenceTransformers
with a lightweight TF-IDF Cosine-Similarity fallback.

Maps input queries to semantic intent vectors for natural language understanding.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

# Ensure project root is in sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorIntentClassifier:
    """
    Vector database-backed intent classifier using semantic vector search.
    """

    def __init__(
        self,
        db_dir: Path = Settings.MODELS_DIR / "chroma_db",
        collection_name: str = "orion_intents",
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.db_dir = db_dir
        self.collection_name = collection_name
        self.model_name = model_name

        self._backend = "none"  # "chroma" or "scikit"
        self._client = None
        self._collection = None
        self._embedder = None

        # Fallback scikit components
        self._vectoriser = None
        self._example_vectors = None
        self._intents_list = []
        self._examples_list = []

    def load(self) -> None:
        """Load persistent vector database or vector similarity fallback."""
        try:
            import chromadb
            self.db_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self.db_dir))
            try:
                self._collection = self._client.get_collection(name=self.collection_name)
                self._backend = "chroma"
                logger.info(f"Loaded persistent ChromaDB collection '{self.collection_name}'.")
                return
            except Exception:
                logger.info("ChromaDB collection not found. Initializing training...")
                self.train()
                return
        except ImportError as e:
            logger.warning(f"ChromaDB/SentenceTransformers not fully ready ({e}). Using Lightweight Vector Similarity Engine.")
            self._init_lightweight_vector_engine()

    def _init_lightweight_vector_engine(self):
        from sklearn.feature_extraction.text import TfidfVectorizer

        json_file = Settings.DATA_DIR / "training_data.json"
        if not json_file.exists():
            logger.error(f"Training data not found at {json_file}")
            return

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._examples_list = []
        self._intents_list = []

        for intent_info in data.get("intents", []):
            intent = intent_info.get("intent")
            examples = intent_info.get("examples", [])
            for ex in examples:
                self._examples_list.append(ex)
                self._intents_list.append(intent)

        if not self._examples_list:
            return

        self._vectoriser = TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True)
        self._example_vectors = self._vectoriser.fit_transform(self._examples_list)
        self._backend = "scikit"
        logger.info(f"Lightweight Vector Similarity Engine pre-indexed {len(self._examples_list)} intent vectors.")

    def train(self, json_path: Path | str = Settings.DATA_DIR / "training_data.json") -> dict[str, Any]:
        """
        Populate vector database from training data.
        """
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            if self._embedder is None:
                logger.info(f"Loading SentenceTransformer model '{self.model_name}'...")
                self._embedder = SentenceTransformer(self.model_name)

            self.db_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self.db_dir))

            try:
                self._client.delete_collection(name=self.collection_name)
            except Exception:
                pass

            self._collection = self._client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            json_file = Path(json_path)
            documents: list[str] = []
            metadatas: list[dict[str, str]] = []
            ids: list[str] = []

            counter = 0
            if json_file.exists():
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for intent_info in data.get("intents", []):
                    intent = intent_info.get("intent")
                    for example in intent_info.get("examples", []):
                        documents.append(example)
                        metadatas.append({"intent": intent})
                        ids.append(f"doc_{counter}")
                        counter += 1

            if documents:
                logger.info(f"Generating vector embeddings for {len(documents)} intent examples...")
                embeddings = self._embedder.encode(documents).tolist()

                self._collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids,
                )
                self._backend = "chroma"
                logger.info(f"ChromaDB Vector collection populated with {len(documents)} items.")
            return {"num_samples": len(documents)}
        except Exception as e:
            logger.warning(f"Failed ChromaDB train ({e}). Initializing Lightweight Vector Engine.")
            self._init_lightweight_vector_engine()
            return {"num_samples": len(self._examples_list)}

    def predict(self, text: str) -> tuple[str, float]:
        """
        Query vector database or similarity engine for nearest semantic intent match.

        Returns:
            (intent_label, similarity_score)
        """
        text_clean = text.strip()
        if not text_clean:
            return ("UNKNOWN", 0.0)

        if self._backend == "none":
            self.load()

        if self._backend == "chroma" and self._collection is not None:
            if self._embedder is None:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer(self.model_name)

            query_embedding = self._embedder.encode([text_clean]).tolist()
            results = self._collection.query(query_embeddings=query_embedding, n_results=1)

            if results and results.get("metadatas") and results["metadatas"][0]:
                intent_label = results["metadatas"][0][0]["intent"]
                distance = results["distances"][0][0] if results.get("distances") else 1.0
                # ChromaDB cosine distance is in [0, 2]. Convert to similarity in [0, 1].
                similarity = max(0.0, 1.0 - (distance / 2.0))

                if similarity < 0.68:
                    logger.info(f"ChromaDB Vector match too low: similarity={similarity:.2%} (threshold=68.0%) for input '{text}'")
                    return ("UNKNOWN", 0.0)

                logger.info(f"ChromaDB Vector match: intent='{intent_label}' (similarity={similarity:.2%}) for input '{text}'")
                return (intent_label, float(similarity))

        if self._backend == "scikit" and self._vectoriser is not None:
            from sklearn.metrics.pairwise import cosine_similarity
            query_vec = self._vectoriser.transform([text_clean])
            sims = cosine_similarity(query_vec, self._example_vectors)[0]
            max_idx = int(np.argmax(sims))
            similarity = float(sims[max_idx])

            if similarity < 0.35:
                logger.info(f"Lightweight Vector match too low: similarity={similarity:.2%} (threshold=35.0%) for input '{text}'")
                return ("UNKNOWN", 0.0)

            intent_label = self._intents_list[max_idx]

            logger.info(f"Lightweight Vector match: intent='{intent_label}' (similarity={similarity:.2%}) for input '{text}'")
            return (intent_label, similarity)

        return ("UNKNOWN", 0.0)
