"""HTML helper utilities used by scrapers."""

from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.sections.aliases import DOMAIN_SECTION_ALIASES
from scrapers.wiki.parsers.section_detection import find_section_heading

_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_HEADING_AND_TABLE_TAGS = [*list(_HEADING_TAGS), "table"]

def find_section_elements(
    soup: BeautifulSoup,
    section_id: str | None,
    target_tags: Iterable[str],
    *,
    domain: str | None = None,
    **kwargs: Any,
) -> list[Tag]:
    """Find elements after a section heading or across the whole document.

    When ``section_id`` is provided, the search starts after the heading with
    the matching id/text/alias. Otherwise, all matching elements in the soup are returned.
    Additional ``kwargs`` are forwarded to ``find_all`` / ``find_all_next``.
    """
    if section_id:
        heading = find_heading(soup, section_id, domain=domain)
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
    domain: str | None = None,
) -> list[Tag]:
    """Find all tables within a section.

    Stop at the next heading of equal or higher level.

    Unlike ``find_section_elements``, this function respects section boundaries
    and does not return tables from subsequent sections.

    Works with both old Wikipedia structure (``<h2><span id="…">``…``</span></h2>``)
    and modern Wikipedia structure where headings are wrapped in
    ``<div class="mw-heading">`` and the id may be placed directly on the ``<h2>`` /
    ``<h3>`` element rather than on an inner span.

    Raises ``RuntimeError`` if the section is not found.
    """
    heading = find_heading(soup, section_id, domain=domain)
    if not heading:
        msg = f"Nie znaleziono sekcji o id={section_id!r}"
        raise RuntimeError(msg)

    current_level = int(heading.name[1])

    tables: list[Tag] = []
    for element in heading.find_all_next(_HEADING_AND_TABLE_TAGS):
        if element.name in _HEADING_TAGS:
            if int(element.name[1]) <= current_level:
                break
        elif element.name == "table":
            if class_ in (element.get("class") or []):
                tables.append(element)
    return tables


def find_heading(
    soup: BeautifulSoup,
    section_id: str,
    *,
    aliases: Mapping[str, set[str]] | None = None,
    domain: str | None = None,
) -> Tag | None:
    match = find_section_heading(
        soup,
        section_id,
        aliases=aliases,
        domain=domain,
        domain_aliases=DOMAIN_SECTION_ALIASES,
    )
    if not match:
        return None
    return match.heading


def find_heading_by_text(soup: BeautifulSoup, section_id: str) -> Tag | None:
    return find_heading(soup, section_id)
