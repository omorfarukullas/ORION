"""
nlp/command_dispatcher.py
=========================
Routes ParsedCommand objects to their corresponding action functions
and returns spoken confirmation strings.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict

from actions import applications, browser, files, media, screenshots, system
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


def get_time() -> str:
    """Return spoken current time."""
    now = datetime.now()
    time_str = now.strftime("%I:%M %p").lstrip("0")
    return f"The time is {time_str}."


def get_date() -> str:
    """Return spoken current date."""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    return f"Today is {date_str}."


def _get_entity_val(entities: Dict[str, Any], key: str, fallback_entity: str | None = None) -> str:
    val = entities.get(key)
    if val:
        return str(val)
    if fallback_entity:
        return fallback_entity
    return ""


def dispatch_action(intent: str, entities: Dict[str, Any], fallback_entity: str | None = None) -> str:
    """
    Execute action corresponding to *intent* and *entities*.
    """
    match intent:
        case "TIME":
            return get_time()
        case "DATE":
            return get_date()
        case "SCREENSHOT":
            return screenshots.take_screenshot()
        case "OPEN_APP":
            app_name = _get_entity_val(entities, "app_name", fallback_entity)
            return applications.open_application(app_name)
        case "CLOSE_APP":
            app_name = _get_entity_val(entities, "app_name", fallback_entity)
            return applications.close_application(app_name)
        case "OPEN_WEBSITE":
            url = _get_entity_val(entities, "url", fallback_entity)
            return browser.open_url(url)
        case "WEB_SEARCH":
            query = _get_entity_val(entities, "query", fallback_entity)
            return browser.web_search(query)
        case "YOUTUBE_SEARCH":
            query = _get_entity_val(entities, "query", fallback_entity)
            return browser.youtube_search(query)
        case "SYSTEM_CPU":
            return system.get_cpu_usage()
        case "SYSTEM_RAM":
            return system.get_ram_usage()
        case "SYSTEM_BATTERY":
            return system.get_battery_status()
        case "SYSTEM_INFO":
            return system.get_system_info()
        case "CREATE_FOLDER":
            folder_name = _get_entity_val(entities, "folder_name", fallback_entity)
            return files.create_folder(folder_name)
        case "CREATE_FILE":
            file_name = _get_entity_val(entities, "file_name", fallback_entity)
            return files.create_file(file_name)
        case "FIND_FILE":
            file_name = _get_entity_val(entities, "file_name", fallback_entity)
            return files.find_file(file_name)
        case "RENAME_FILE":
            old_name = _get_entity_val(entities, "old_name")
            new_name = _get_entity_val(entities, "new_name")
            return files.rename_file(old_name, new_name)
        case "DELETE_FILE":
            file_name = _get_entity_val(entities, "file_name", fallback_entity)
            return files.delete_file(file_name)
        case "PLAY_MEDIA":
            return media.play_media()
        case "PAUSE_MEDIA":
            return media.pause_media()
        case "NEXT_TRACK":
            return media.next_track()
        case "PREVIOUS_TRACK":
            return media.previous_track()
        case "VOLUME_UP":
            return media.volume_up()
        case "VOLUME_DOWN":
            return media.volume_down()
        case "MUTE":
            return media.mute()
        case _:
            logger.info(f"Unhandled intent '{intent}'")
            return "Sorry, I did not understand that command."


def dispatch(cmd: Any) -> str:
    """
    Route *cmd* (ParsedCommand object) to the correct execution function with confidence gating.

    Args:
        cmd: ParsedCommand object containing intent, confidence, and entities.

    Returns:
        Spoken response string.
    """
    intent = getattr(cmd, "intent", "UNKNOWN")
    confidence = getattr(cmd, "confidence", 1.0)
    entities = getattr(cmd, "entities", {})
    fallback_entity = getattr(cmd, "entity", None)
    raw_text = getattr(cmd, "raw_text", "")

    logger.info(f"Gating dispatch for intent '{intent}' at confidence {confidence:.2%}")

    if confidence >= Settings.CONFIDENCE_EXECUTE:
        return dispatch_action(intent, entities, fallback_entity)
    elif confidence >= Settings.CONFIDENCE_CONFIRM:
        logger.warning(
            f"Medium confidence ({confidence:.2%}) for intent '{intent}'. Executing with user notice."
        )
        result = dispatch_action(intent, entities, fallback_entity)
        return f"I think you meant {intent.replace('_', ' ').lower()}. {result}"
    else:
        logger.warning(f"Low confidence ({confidence:.2%}) for intent '{intent}'. Aborting execution.")
        return "I am not confident I understood your command. Please try again."


def dispatch_with_confidence(
    intent: str,
    confidence: float,
    entity: str | None,
    raw_text: str,
) -> str:
    """
    Legacy wrapper for dispatch with raw parameters.
    """
    class DummyCmd:
        pass

    d = DummyCmd()
    d.intent = intent
    d.confidence = confidence
    d.entity = entity
    d.entities = {}
    d.raw_text = raw_text
    return dispatch(d)
