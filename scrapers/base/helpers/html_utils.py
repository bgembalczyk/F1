"""HTML helper utilities used by scrapers."""

from collections.abc import Iterable
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text

_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_HEADING_AND_TABLE_TAGS = list(_HEADING_TAGS) + ["table"]


def find_section_elements(
    soup: BeautifulSoup,
    section_id: str | None,
    target_tags: Iterable[str],
    **kwargs: Any,
) -> list[Tag]:
    """Find elements after a section heading or across the whole document.

    When ``section_id`` is provided, the search starts after the heading with
    the matching id. Otherwise, all matching elements in the soup are returned.
    Additional ``kwargs`` are forwarded to ``find_all`` / ``find_all_next``.
    """
    if section_id:
        heading = soup.find(id=section_id)
        if not heading:
            heading = find_heading_by_text(soup, section_id)
        if not heading:
            msg = f"Nie znaleziono sekcji o id={section_id!r}"
            raise RuntimeError(msg)

        return list(heading.find_all_next(target_tags, **kwargs))

    return list(soup.find_all(target_tags, **kwargs))


def find_section_tables(
    soup: BeautifulSoup,
    section_id: str,
    *,
    class_: str = "wikitable",
) -> list[Tag]:
    """Find all tables within a section, stopping at the next heading of equal or higher level.

    Unlike ``find_section_elements``, this function respects section boundaries
    and does not return tables from subsequent sections.

    Works with both old Wikipedia structure (``<h2><span id="…">``…``</span></h2>``)
    and modern Wikipedia structure where headings are wrapped in
    ``<div class="mw-heading">`` and the id may be placed directly on the ``<h2>`` /
    ``<h3>`` element rather than on an inner span.

    Raises ``RuntimeError`` if the section is not found.
    """
    heading = soup.find(id=section_id)
    if not heading:
        heading = find_heading_by_text(soup, section_id)
    if not heading:
        msg = f"Nie znaleziono sekcji o id={section_id!r}"
        raise RuntimeError(msg)

    # Determine this section's heading level so we can stop at the next peer section.
    section_heading = (
        heading if heading.name in _HEADING_TAGS else heading.find_parent(_HEADING_TAGS)
    )
    if section_heading is None:
        # No enclosing h-tag found — return all following tables without level-based stopping.
        return [
            t
            for t in heading.find_all_next("table")
            if class_ in (t.get("class") or [])
        ]

    current_level = int(section_heading.name[1])

    # Traverse the document in order starting from the heading anchor.
    # We look for tables and stop as soon as we hit a heading of equal or higher level.
    # Using find_all_next from `heading` (rather than find_next_siblings from
    # section_heading) makes this robust to wrapper elements like
    # <div class="mw-heading"> that may surround the <hN> tag.
    tables: list[Tag] = []
    for element in heading.find_all_next(_HEADING_AND_TABLE_TAGS):
        if element.name in _HEADING_TAGS:
            if int(element.name[1]) <= current_level:
                break
        elif element.name == "table":
            if class_ in (element.get("class") or []):
                tables.append(element)
    return tables


def find_heading_by_text(soup: BeautifulSoup, section_id: str) -> Tag | None:
    normalized_id = normalize_heading_text(section_id)
    if not normalized_id:
        return None

    for headline in soup.select(".mw-headline"):
        headline_text = normalize_heading_text(headline.get_text(" ", strip=True))
        if headline_text == normalized_id:
            return headline

    return None


def normalize_heading_text(text: str) -> str:
    return clean_wiki_text(text.replace("_", " ")).lower().strip()
