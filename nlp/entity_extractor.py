"""
nlp/entity_extractor.py
=======================
Phase 7 — Entity Extraction

Rule-based entity extraction. Pulls app names, URLs, file names, search
queries, and other slot values out of a command string using regex and keyword rules.
"""
from __future__ import annotations
import re
from typing import Dict, Any


class EntityExtractor:
    """
    Extracts named entities from a classified command string.
    """

    def extract(self, text: str, intent: str) -> Dict[str, Any]:
        """
        Extract entities relevant to *intent* from *text*.

        Args:
            text:   Command string.
            intent: Intent label from the classifier.

        Returns:
            Dict of entity_name → value.
        """
        text = text.strip()
        entities: Dict[str, Any] = {}

        if not text or not intent:
            return entities

        if intent in ("OPEN_APP", "CLOSE_APP"):
            app_match = re.sub(r"^(open|launch|start|run|close|quit|kill|exit|stop)\s+", "", text, flags=re.IGNORECASE).strip()
            if app_match:
                entities["app_name"] = app_match

        elif intent == "OPEN_WEBSITE":
            match = re.sub(r"^(open|go to|navigate to|visit|launch)\s+", "", text, flags=re.IGNORECASE).strip()
            if match:
                entities["url"] = match

        elif intent == "WEB_SEARCH":
            query = re.sub(r"^(search|google|find|look up)\s+(google\s+for\s+|for\s+)?", "", text, flags=re.IGNORECASE).strip()
            if query:
                entities["query"] = query

        elif intent == "YOUTUBE_SEARCH":
            query = re.sub(r"^(search\s+youtube\s+for|youtube\s+search\s+for|youtube\s+search|play|search\s+on\s+youtube\s+for)\s+", "", text, flags=re.IGNORECASE).strip()
            if query:
                entities["query"] = query

        elif intent == "CREATE_FOLDER":
            # "create a folder called AI Projects" -> "AI Projects"
            match = re.search(r"(?:called|named)\s+(.+)$", text, flags=re.IGNORECASE)
            if match:
                entities["folder_name"] = match.group(1).strip()
            else:
                folder = re.sub(r"^(create|make|new)\s+(a\s+)?(folder|directory)\s*", "", text, flags=re.IGNORECASE).strip()
                if folder:
                    entities["folder_name"] = folder

        elif intent == "CREATE_FILE":
            # "create a file called note.txt" -> "note.txt"
            match = re.search(r"(?:called|named)\s+(.+)$", text, flags=re.IGNORECASE)
            if match:
                entities["file_name"] = match.group(1).strip()
            else:
                file_name = re.sub(r"^(create|make|new)\s+(a\s+)?file\s*", "", text, flags=re.IGNORECASE).strip()
                if file_name:
                    entities["file_name"] = file_name

        elif intent == "FIND_FILE":
            match = re.sub(r"^(find|locate|search for|where is)\s+(the\s+)?(file\s+)?", "", text, flags=re.IGNORECASE).strip()
            if match:
                entities["file_name"] = match

        elif intent == "RENAME_FILE":
            match = re.search(r"rename\s+(?:file\s+)?(.+?)\s+(?:to|as)\s+(.+)$", text, flags=re.IGNORECASE)
            if match:
                entities["old_name"] = match.group(1).strip()
                entities["new_name"] = match.group(2).strip()

        elif intent == "DELETE_FILE":
            match = re.sub(r"^(delete|remove|erase|trash)\s+(the\s+)?(file|folder|directory\s+)?", "", text, flags=re.IGNORECASE).strip()
            if match:
                entities["file_name"] = match

        return entities
