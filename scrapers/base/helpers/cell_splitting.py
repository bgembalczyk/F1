"""Utilities for splitting HTML table cells on <br> tags."""

import re
from typing import List

from bs4 import BeautifulSoup, Tag


def split_cell_on_br(cell: Tag, *, replace_link_breaks: bool = False) -> List[Tag]:
    """
    Splits a cell into segments on <br> tags. If no <br> tags are found, returns [cell].

    Each segment is a new artificial <span> tag to allow independent counting of text and links
    without modifying the original DOM tree.

    Args:
        cell: The HTML table cell to split.
        replace_link_breaks: If True, replaces <br> tags inside <a> tags with spaces before splitting.

    Returns:
        A list of Tag elements, one for each segment.
    """
    html = cell.decode_contents()
    
    if replace_link_breaks:
        html = _replace_link_breaks(html)
    
    parts = re.split(r"<br\s*/?>", html, flags=re.IGNORECASE)

    segments: List[Tag] = []
    soup = cell.soup or BeautifulSoup("", "html.parser")

    for part in parts:
        if not part.strip():
            continue
        frag_soup = BeautifulSoup(part, "html.parser")
        span = soup.new_tag("span")
        for el in list(frag_soup.contents):
            span.append(el)
        segments.append(span)

    return segments or [cell]


def split_cell_on_br_dom_based(cell: Tag) -> List[Tag]:
    """
    Splits a cell on <br> tags using DOM-based parsing.

    This variant iterates through the cell's contents and groups them by <br> separators.
    It's useful when you need to preserve the exact structure of the original content.

    Args:
        cell: The HTML table cell to split.

    Returns:
        A list of Tag elements, one for each segment.
    """
    html = cell.decode_contents()
    frag_soup = BeautifulSoup(html, "html.parser")
    segments: List[List[Tag]] = [[]]

    for node in list(frag_soup.contents):
        if isinstance(node, Tag) and node.name == "br":
            if segments[-1]:
                segments.append([])
            continue
        segments[-1].append(node)

    wrapped: List[Tag] = []
    for segment in segments:
        if not segment:
            continue
        span = frag_soup.new_tag("span")
        for el in segment:
            span.append(el)
        wrapped.append(span)

    return wrapped or [cell]


def split_cell_on_br_with_children(cell: Tag) -> List[Tag]:
    """
    Splits a cell on <br> tags by iterating through direct children.

    This variant is optimized for cells where <br> tags are direct children
    rather than nested deep in the structure.

    Args:
        cell: The HTML table cell to split.

    Returns:
        A list of Tag elements, one for each segment.
    """
    parts: List[str] = []
    current: List[str] = []

    for child in list(cell.contents):
        if isinstance(child, Tag) and child.name and child.name.lower() == "br":
            if current:
                parts.append("".join(current))
                current = []
            continue
        current.append(str(child))

    if current:
        parts.append("".join(current))

    if not parts:
        html = cell.decode_contents()
        parts = re.split(r"<br\s*/?>", html, flags=re.IGNORECASE)
    
    segments: List[Tag] = []
    soup = cell.soup or BeautifulSoup("", "html.parser")

    for part in parts:
        if not part.strip():
            continue
        frag_soup = BeautifulSoup(part, "html.parser")
        span = soup.new_tag("span")
        for el in list(frag_soup.contents):
            span.append(el)
        segments.append(span)

    return segments or [cell]


def _replace_link_breaks(html: str) -> str:
    """
    Replaces <br> tags inside <a> tags with spaces.

    Args:
        html: The HTML string to process.

    Returns:
        The processed HTML string.
    """
    fragment = BeautifulSoup(html, "html.parser")
    for br in fragment.find_all("br"):
        if br.find_parent("a"):
            br.replace_with(" ")
    return str(fragment)
