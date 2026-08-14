"""
nlp/command_dispatcher.py
=========================
Routes ParsedCommand objects to their corresponding action function
and returns the spoken confirmation string.
"""
from __future__ import annotations
from datetime import datetime

from actions import applications, browser, media, screenshots, system
from config.settings import Settings
from nlp.rule_engine import ParsedCommand
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


def dispatch(cmd: ParsedCommand) -> str:
    """
    Route *cmd* to the correct execution function.

    Args:
        cmd: ParsedCommand instance from RuleEngine or NLP parser.

    Returns:
        Spoken response string.
    """
    logger.info(f"Dispatching intent '{cmd.intent}' (entity='{cmd.entity}')")

    match cmd.intent:
        case "TIME":
            return get_time()
        case "DATE":
            return get_date()
        case "SCREENSHOT":
            return screenshots.take_screenshot()
        case "OPEN_APP":
            return applications.open_application(cmd.entity or "")
        case "WEB_SEARCH":
            return browser.web_search(cmd.entity or "")
        case "YOUTUBE_SEARCH":
            return browser.youtube_search(cmd.entity or "")
        case "SYSTEM_CPU":
            return system.get_cpu_usage()
        case "SYSTEM_RAM":
            return system.get_ram_usage()
        case "SYSTEM_BATTERY":
            return system.get_battery_status()
        case "VOLUME_UP":
            return media.volume_up()
        case "VOLUME_DOWN":
            return media.volume_down()
        case "MUTE":
            return media.mute()
        case _:
            logger.info(f"Unhandled intent '{cmd.intent}' for command '{cmd.raw_text}'")
            return "Sorry, I did not understand that command."


def dispatch_with_confidence(
    intent: str,
    confidence: float,
    entity: str | None,
    raw_text: str,
) -> str:
    """
    Dispatch intent with confidence threshold validation (Operating Rule 5).

    Thresholds:
        - > 80% (CONFIDENCE_EXECUTE): Execute immediately.
        - 50%-80% (CONFIDENCE_CONFIRM): Log warning and execute with confirmation prefix.
        - < 50%: Ask for clarification.
    """
    logger.info(f"Gating dispatch for intent '{intent}' at confidence {confidence:.2%}")

    if confidence >= Settings.CONFIDENCE_EXECUTE:
        cmd = ParsedCommand(intent=intent, entity=entity, raw_text=raw_text)
        return dispatch(cmd)
    elif confidence >= Settings.CONFIDENCE_CONFIRM:
        logger.warning(
            f"Medium confidence ({confidence:.2%}) for intent '{intent}'. Executing with user notice."
        )
        cmd = ParsedCommand(intent=intent, entity=entity, raw_text=raw_text)
        result = dispatch(cmd)
        return f"I think you meant {intent.replace('_', ' ').lower()}. {result}"
    else:
        logger.warning(f"Low confidence ({confidence:.2%}) for intent '{intent}'. Aborting execution.")
        return "I am not confident I understood your command. Please try again."
