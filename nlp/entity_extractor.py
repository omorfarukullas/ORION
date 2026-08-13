"""
nlp/entity_extractor.py
=======================
STUB — Phase 7

Rule-based entity extraction. Pulls app names, URLs, file names, search
queries, and other slot values out of a command string.
"""
from __future__ import annotations
from typing import Dict, Any


class EntityExtractor:
    """
    Extracts named entities from a classified command.

    Example (Phase 7):
        "open chrome"  →  {"app_name": "chrome"}
        "search youtube for lofi music"  →  {"query": "lofi music"}
        "create a folder called AI Projects"  →  {"folder_name": "AI Projects"}

    Approach: regex + keyword matching (no ML), keeping extraction fast
    and fully local. A spaCy NER model is an optional upgrade for V2.
    """

    def extract(self, text: str, intent: str) -> Dict[str, Any]:
        """
        Extract entities relevant to *intent* from *text*.

        Args:
            text:    Preprocessed command string.
            intent:  Intent label from the classifier.

        Returns:
            Dict of entity_name → value.

        Raises:
            NotImplementedError: Until Phase 7 is implemented.
        """
        raise NotImplementedError("EntityExtractor is implemented in Phase 7.")
