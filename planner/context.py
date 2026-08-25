"""
planner/context.py
==================
Phase 11 — Short-Term Conversational Context

Short-term context memory: tracks recent intents, entities, applications,
and queries so follow-up commands resolve seamlessly.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
from nlp.command_parser import ParsedCommand
from utils.logger import get_logger

logger = get_logger(__name__)


class ConversationContext:
    """
    Tracks the most recent command's intent, entities, and open applications
    to resolve ambiguous follow-up commands.
    """

    def __init__(self) -> None:
        self.last_intent: Optional[str] = None
        self.last_entity: Optional[str] = None
        self.last_application: Optional[str] = None
        self.last_search_query: Optional[str] = None
        self.last_file: Optional[str] = None
        self.last_folder: Optional[str] = None

    def update(self, parsed_cmd: ParsedCommand) -> None:
        """
        Update conversation context after a command execution.
        """
        self.last_intent = parsed_cmd.intent
        entities = parsed_cmd.entities or {}

        if "app_name" in entities and entities["app_name"] not in ("it", "close", "open", "the app", "that"):
            self.last_application = entities["app_name"]
            self.last_entity = entities["app_name"]

        if "query" in entities and entities["query"] not in ("it", "that", "this"):
            self.last_search_query = entities["query"]
            self.last_entity = entities["query"]

        if "file_name" in entities and entities["file_name"] not in ("it", "the file", "that"):
            self.last_file = entities["file_name"]
            self.last_entity = entities["file_name"]

        if "folder_name" in entities:
            self.last_folder = entities["folder_name"]
            self.last_entity = entities["folder_name"]

        logger.debug(f"Context updated: {self}")

    def resolve(self, parsed_cmd: ParsedCommand) -> ParsedCommand:
        """
        Resolve missing entities or follow-up references using context.

        Examples:
            - Intent is OPEN_APP / CLOSE_APP but entity is missing / "it" -> use last_application
            - Intent is WEB_SEARCH / YOUTUBE_SEARCH but query is missing / "it" -> use last_search_query / last_entity
            - Intent is DELETE_FILE / FIND_FILE but file_name is missing / "it" -> use last_file
        """
        entities = dict(parsed_cmd.entities or {})
        raw_lower = parsed_cmd.raw_text.lower().strip()

        # Follow-up app resolution: "close it", "close", "quit it", "open it"
        if parsed_cmd.intent in ("OPEN_APP", "CLOSE_APP"):
            app_val = entities.get("app_name", "").lower()
            if (not app_val or app_val in ("it", "the app", "that", "close", "open", "quit", "exit")) and self.last_application:
                logger.info(f"Resolved app '{app_val}' to previous app '{self.last_application}'")
                entities["app_name"] = self.last_application

        # Follow-up search resolution: "search for it on youtube", "google it"
        elif parsed_cmd.intent in ("WEB_SEARCH", "YOUTUBE_SEARCH"):
            query_val = entities.get("query", "").lower()
            if (not query_val or query_val in ("it", "that", "this")) and (self.last_search_query or self.last_entity):
                resolved_query = self.last_search_query or self.last_entity
                logger.info(f"Resolved search query '{query_val}' to '{resolved_query}'")
                entities["query"] = resolved_query

        # Follow-up file resolution: "delete it", "find it"
        elif parsed_cmd.intent in ("FIND_FILE", "DELETE_FILE"):
            file_val = entities.get("file_name", "").lower()
            if (not file_val or file_val in ("it", "the file", "that")) and self.last_file:
                logger.info(f"Resolved file '{file_val}' to '{self.last_file}'")
                entities["file_name"] = self.last_file

        return ParsedCommand(
            raw_text=parsed_cmd.raw_text,
            intent=parsed_cmd.intent,
            confidence=parsed_cmd.confidence,
            entities=entities,
        )

    def clear(self) -> None:
        """Reset context."""
        self.last_intent = None
        self.last_entity = None
        self.last_application = None
        self.last_search_query = None
        self.last_file = None
        self.last_folder = None
        logger.debug("Context cleared.")

    def __repr__(self) -> str:
        return (
            f"<ConversationContext intent={self.last_intent!r} "
            f"app={self.last_application!r} query={self.last_search_query!r} "
            f"file={self.last_file!r}>"
        )
