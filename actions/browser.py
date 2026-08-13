"""
actions/browser.py
==================
STUB — Phase 8

Web search and URL navigation using the standard library ``webbrowser``
module (cross-platform, no browser automation needed for basic searches).
"""
from __future__ import annotations


def open_url(url: str) -> str:
    """
    Open *url* in the default browser.

    Args:
        url: Fully-qualified URL, e.g. "https://github.com".

    Returns:
        Spoken confirmation string.

    Raises:
        NotImplementedError: Until Phase 8 is implemented.
    """
    raise NotImplementedError("open_url is implemented in Phase 8.")


def web_search(query: str) -> str:
    """
    Open a Google search for *query* in the default browser.

    Raises:
        NotImplementedError: Until Phase 8 is implemented.
    """
    raise NotImplementedError("web_search is implemented in Phase 8.")


def youtube_search(query: str) -> str:
    """
    Open a YouTube search for *query* in the default browser.

    Raises:
        NotImplementedError: Until Phase 8 is implemented.
    """
    raise NotImplementedError("youtube_search is implemented in Phase 8.")
