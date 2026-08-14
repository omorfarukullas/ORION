"""
nlp/rule_engine.py
==================
Keyword and rule-based intent parser for Phase 5.
Used before the ML intent classifier (Phase 6) is trained.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedCommand:
    intent: str
    entity: str | None
    raw_text: str


class RuleEngine:
    """
    Rule-based engine matching transcripts against keyword patterns in commands.json.
    """

    def __init__(self, commands_path: Path = Settings.CONFIG_DIR / "commands.json") -> None:
        self.commands_path = commands_path
        self.patterns: list[dict] = []
        self.load_patterns()

    def load_patterns(self) -> None:
        """Load pattern rules from commands.json."""
        if not self.commands_path.exists():
            logger.error(f"Commands config file not found at {self.commands_path}")
            return

        try:
            with open(self.commands_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.patterns = data.get("patterns", [])
            logger.info(f"Loaded {len(self.patterns)} command pattern rules from {self.commands_path.name}")
        except Exception as e:
            logger.error(f"Failed to load commands.json: {e}")

    def parse(self, transcript: str) -> ParsedCommand:
        """
        Parse raw transcription text into an intent and entity.

        Args:
            transcript: Raw transcribed string from STT.

        Returns:
            ParsedCommand object containing intent, entity, and raw text.
        """
        text = transcript.strip().lower()
        if not text:
            return ParsedCommand(intent="UNKNOWN", entity=None, raw_text=transcript)

        for pattern in self.patterns:
            intent = pattern.get("intent", "UNKNOWN")
            keywords = pattern.get("keywords", [])
            entity_rule = pattern.get("entity")

            for kw in keywords:
                kw_lower = kw.lower()
                if kw_lower in text:
                    entity = None
                    if entity_rule == "__extract__":
                        idx = text.find(kw_lower)
                        extracted = text[idx + len(kw_lower):].strip()
                        for prefix in ["for", "to", "the", "a"]:
                            if extracted.startswith(prefix + " "):
                                extracted = extracted[len(prefix) + 1:].strip()
                        entity = extracted if extracted else None

                    logger.info(f"RuleEngine matched intent '{intent}' with keyword '{kw}' (entity='{entity}')")
                    return ParsedCommand(intent=intent, entity=entity, raw_text=transcript)

        logger.info(f"RuleEngine found no pattern match for '{transcript}'. Returning UNKNOWN.")
        return ParsedCommand(intent="UNKNOWN", entity=None, raw_text=transcript)
