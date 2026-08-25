"""
nlp/command_parser.py
=====================
Phase 7 — Command Parser Pipeline

Combines preprocessing, intent classification, and entity extraction into a single
parsed-command object ready for the task planner and command dispatcher.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any

from nlp.preprocessing import preprocess
from nlp.intent_classifier import IntentClassifier
from nlp.entity_extractor import EntityExtractor
from nlp.rule_engine import RuleEngine
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedCommand:
    """The output of the NLP pipeline — everything the planner needs."""
    raw_text: str
    intent: str
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"ParsedCommand(intent={self.intent!r}, "
            f"confidence={self.confidence:.0%}, entities={self.entities})"
        )


class CommandParser:
    """
    Orchestrates preprocessing → intent classification → entity extraction.
    """

    def __init__(self) -> None:
        self.classifier = IntentClassifier()
        self.extractor = EntityExtractor()
        self.rule_engine = RuleEngine()

        self.use_ml = False
        try:
            self.classifier.load()
            self.use_ml = True
            logger.info("CommandParser: ML IntentClassifier successfully loaded.")
        except Exception as e:
            logger.warning(f"CommandParser: Could not load ML classifier ({e}). Falling back to RuleEngine.")

    def parse(self, raw_text: str) -> ParsedCommand:
        """
        Parse *raw_text* into a ParsedCommand.

        Args:
            raw_text: Raw input text from speech-to-text.

        Returns:
            ParsedCommand instance containing intent, confidence, and extracted entities.
        """
        intent = "UNKNOWN"
        confidence = 0.0

        if self.use_ml:
            try:
                intent, confidence = self.classifier.predict(raw_text)
            except Exception as e:
                logger.error(f"Error predicting intent with ML classifier: {e}")
                self.use_ml = False

        if not self.use_ml or intent == "UNKNOWN":
            rule_cmd = self.rule_engine.parse(raw_text)
            intent = rule_cmd.intent
            confidence = 1.0 if intent != "UNKNOWN" else 0.0

        # Pass raw_text to entity_extractor so stop-words/structure are intact
        entities = self.extractor.extract(raw_text, intent)

        # Fallback entity filling if entity_extractor returned empty but rule_engine found an entity
        if not entities:
            rule_cmd = self.rule_engine.parse(raw_text)
            if rule_cmd.entity:
                if intent in ("OPEN_APP", "CLOSE_APP"):
                    entities["app_name"] = rule_cmd.entity
                elif intent in ("WEB_SEARCH", "YOUTUBE_SEARCH"):
                    entities["query"] = rule_cmd.entity

        parsed = ParsedCommand(
            raw_text=raw_text,
            intent=intent,
            confidence=confidence,
            entities=entities,
        )
        logger.info(f"Parsed command: {parsed}")
        return parsed
