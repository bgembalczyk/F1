"""Utilities for splitting HTML table cells on <br> tags."""

import re

from bs4 import BeautifulSoup
from bs4 import Tag


def split_cell_on_br(cell: Tag, *, replace_link_breaks: bool = False) -> list[Tag]:
    """
    Splits a cell into segments on <br> tags. If no <br> tags are found, returns [cell].

    Each segment is a new artificial <span> tag
    to allow independent counting of text and links
    without modifying the original DOM tree.

    Args:
        cell: The HTML table cell to split.
        replace_link_breaks: If True, replaces <br> tags inside <a> tags
            with spaces before splitting.

    Returns:
        A list of Tag elements, one for each segment.
    """
    html = cell.decode_contents()

    if replace_link_breaks:
        html = _replace_link_breaks(html)

    parts = re.split(r"<br\s*/?>", html, flags=re.IGNORECASE)
    return _wrap_parts_as_spans(parts, cell)


def _wrap_parts_as_spans(parts: list[str], cell: Tag) -> list[Tag]:
    segments: list[Tag] = []
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
