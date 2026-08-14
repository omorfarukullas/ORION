"""
actions/browser.py
==================
Web search and URL navigation using standard library webbrowser.
"""
from __future__ import annotations
import urllib.parse
import webbrowser
from utils.logger import get_logger

logger = get_logger(__name__)


def open_url(url: str) -> str:
    """
    Open *url* in the default browser.

    Args:
        url: Fully-qualified URL, e.g. "https://github.com".

    Returns:
        Spoken confirmation string.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    logger.info(f"Opening URL: {url}")
    webbrowser.open(url)
    return f"Opening {url}."


def web_search(query: str) -> str:
    """
    Open a Google search for *query* in the default browser.
    """
    if not query:
        return "What would you like me to search for?"

    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    logger.info(f"Searching Google for: '{query}' ({url})")
    webbrowser.open(url)
    return f"Searching Google for {query}."


def youtube_search(query: str) -> str:
    """
    Open a YouTube search for *query* in the default browser.
    """
    if not query:
        return "What would you like to search on YouTube?"

    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    logger.info(f"Searching YouTube for: '{query}' ({url})")
    webbrowser.open(url)
    return f"Searching YouTube for {query}."
