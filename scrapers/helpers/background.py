"""Utilities for extracting background color from HTML table cells."""

import re

from bs4 import Tag


def extract_background(cell: Tag) -> str | None:
    """
    Extracts the background color from a table cell.

    Checks both the 'style' attribute
    (for background or background-color CSS properties)
    and the 'bgcolor' attribute.

    Args:
        cell: The HTML table cell element.

    Returns:
        The background color string if found, None otherwise.
    """
    style = cell.get("style") or ""
    if style:
        match = re.search(r"background(?:-color)?\s*:\s*([^;]+)", style, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    bgcolor = cell.get("bgcolor")
    if bgcolor:
        return str(bgcolor).strip()

    return None
