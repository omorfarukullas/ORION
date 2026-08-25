"""
nlp/command_dispatcher.py
=========================
Routes ParsedCommand objects to their corresponding action functions
and returns spoken confirmation strings. Enforces security gating (Phase 9)
and handles persistent memory (Phase 11).
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict

from actions import applications, browser, files, media, screenshots, system, weather, calculator, clipboard, llm
from config.settings import Settings
from security.command_validator import get_risk_level, RiskLevel
from security.permissions import audit_log
from security.confirmation import ConfirmationHandler
from database.database import Database
from utils.logger import get_logger

logger = get_logger(__name__)

# Default global db instance
_db: Database | None = None


def get_db() -> Database:
    global _db
    if _db is None:
        _db = Database(Settings.DB_PATH)
    return _db


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


def dispatch_action(
    intent: str,
    entities: Dict[str, Any],
    fallback_entity: str | None = None,
    db: Database | None = None,
) -> str:
    """
    Execute action corresponding to *intent* and *entities*.
    """
    database = db or get_db()

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
        case "SHUTDOWN":
            return system.shutdown()
        case "RESTART":
            return system.restart()
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
        case "REMEMBER":
            key = _get_entity_val(entities, "key")
            value = _get_entity_val(entities, "value")
            if not key or not value:
                return "What would you like me to remember?"
            database.save_memory(key, value)
            return f"I will remember that {key} is {value}."
        case "RECALL":
            key = _get_entity_val(entities, "key")
            if not key:
                return "What would you like me to recall?"
            val = database.recall_memory(key)
            if val:
                return f"You told me that {key} is {val}."
            else:
                return f"I don't have any memory stored for {key}."
        case "WEATHER":
            loc = _get_entity_val(entities, "location", fallback_entity)
            return weather.get_weather(loc)
        case "CALCULATE":
            expr = _get_entity_val(entities, "expression", fallback_entity)
            return calculator.calculate(expr or fallback_entity or "")
        case "CLIPBOARD_READ":
            return clipboard.read_clipboard()
        case "CLIPBOARD_COPY":
            txt = _get_entity_val(entities, "text", fallback_entity)
            return clipboard.copy_to_clipboard(txt)
        case "CLIPBOARD_CLEAR":
            return clipboard.clear_clipboard()
        case "ASK_ORION":
            q = _get_entity_val(entities, "question", fallback_entity)
            return llm.ask_llm(q or fallback_entity or "")
        case _:
            logger.info(f"Unhandled intent '{intent}'")
            return "Sorry, I did not understand that command."


def dispatch(
    cmd: Any,
    confirmation_handler: ConfirmationHandler | None = None,
    db: Database | None = None,
) -> str:
    """
    Route *cmd* (ParsedCommand object) to the correct execution function with confidence
    gating, security validation (Phase 9), and persistent memory (Phase 11).

    Args:
        cmd: ParsedCommand object containing intent, confidence, and entities.
        confirmation_handler: Optional ConfirmationHandler instance for destructive actions.
        db: Optional Database instance.

    Returns:
        Spoken response string.
    """
    intent = getattr(cmd, "intent", "UNKNOWN")
    confidence = getattr(cmd, "confidence", 1.0)
    entities = getattr(cmd, "entities", {})
    fallback_entity = getattr(cmd, "entity", None)
    raw_text = getattr(cmd, "raw_text", "")

    if intent == "UNKNOWN":
        logger.info(f"Command text '{raw_text}' resulted in UNKNOWN intent.")
        return "Sorry, I did not understand that command."

    # Security check: Risk level
    risk = get_risk_level(intent)
    if risk == RiskLevel.FORBIDDEN:
        logger.warning(f"Forbidden intent '{intent}' requested. Execution blocked.")
        audit_log(intent, str(entities), "FORBIDDEN_BLOCKED")
        return "Sorry, I am not allowed to perform that action."

    if risk == RiskLevel.DESTRUCTIVE:
        logger.warning(f"Destructive intent '{intent}' requested. Confirmation required.")
        description = f"{intent.replace('_', ' ').lower()}"
        entity_val = _get_entity_val(entities, "file_name", fallback_entity) or _get_entity_val(entities, "app_name")
        if entity_val:
            description += f" {entity_val}"

        confirmed = False
        if confirmation_handler:
            confirmed = confirmation_handler.ask(description)
        
        if not confirmed:
            logger.info(f"Execution of destructive intent '{intent}' was not confirmed.")
            audit_log(intent, str(entities), "CANCELLED_BY_USER")
            return "Action cancelled."

    logger.info(f"Gating dispatch for intent '{intent}' at confidence {confidence:.2%}")

    if confidence >= Settings.CONFIDENCE_EXECUTE:
        res = dispatch_action(intent, entities, fallback_entity, db=db)
        audit_log(intent, str(entities), "EXECUTED_SUCCESS")
        return res
    elif confidence >= Settings.CONFIDENCE_CONFIRM:
        logger.warning(
            f"Medium confidence ({confidence:.2%}) for intent '{intent}'. Executing with user notice."
        )
        res = dispatch_action(intent, entities, fallback_entity, db=db)
        audit_log(intent, str(entities), "EXECUTED_MEDIUM_CONFIDENCE")
        return f"I think you meant {intent.replace('_', ' ').lower()}. {res}"
    else:
        logger.warning(f"Low confidence ({confidence:.2%}) for intent '{intent}'. Aborting execution.")
        audit_log(intent, str(entities), "LOW_CONFIDENCE_ABORTED")
        return "I am not confident I understood your command. Please try again."


def dispatch_with_confidence(
    intent: str,
    confidence: float,
    entity: str | None,
    raw_text: str,
    confirmation_handler: ConfirmationHandler | None = None,
    db: Database | None = None,
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
    return dispatch(d, confirmation_handler=confirmation_handler, db=db)
