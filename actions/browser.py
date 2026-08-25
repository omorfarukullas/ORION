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
        url: Fully-qualified URL or website name, e.g. "github.com" or "youtube".

    Returns:
        Spoken confirmation string.
    """
    cleaned = url.strip()
    if not cleaned:
        return "Which website would you like me to open?"

    # Strip phrases like "tab", "website", "page"
    cleaned = urllib.parse.unquote(cleaned)
    import re
    cleaned = re.sub(r"\s+(website|tab|page|site)$", "", cleaned, flags=re.IGNORECASE).strip()

    if not cleaned.startswith(("http://", "https://")):
        if "." not in cleaned:
            cleaned = f"https://www.{cleaned}.com"
        else:
            cleaned = "https://" + cleaned

    logger.info(f"Opening URL: {cleaned}")
    webbrowser.open(cleaned)
    return f"Opening {cleaned}."


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
    Open a YouTube search for *query* in the default browser, or open YouTube homepage if no query.
    """
    cleaned = (query or "").strip()
    if not cleaned or cleaned.lower() in ("open youtube", "open youtube tab", "youtube", "youtube tab", "open youtube website"):
        url = "https://www.youtube.com"
        logger.info(f"Opening YouTube homepage: {url}")
        webbrowser.open(url)
        return "Opening YouTube."

    # Clean redundant command prefixes if present in query
    import re
    clean_query = re.sub(r"^(open\s+youtube\s+(tab\s+)?(and\s+)?(search\s+(for\s+)?)?|search\s+youtube\s+for\s+|youtube\s+search\s+(for\s+)?)", "", cleaned, flags=re.IGNORECASE).strip()
    target_query = clean_query if clean_query else cleaned

    encoded_query = urllib.parse.quote(target_query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    logger.info(f"Searching YouTube for: '{target_query}' ({url})")
    webbrowser.open(url)
    return f"Searching YouTube for {target_query}."
