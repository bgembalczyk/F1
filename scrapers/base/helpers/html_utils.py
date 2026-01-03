"""HTML helper utilities used by scrapers."""

from typing import Any, Iterable

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.text import clean_wiki_text


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
            raise RuntimeError(f"Nie znaleziono sekcji o id={section_id!r}")

        return list(heading.find_all_next(target_tags, **kwargs))

    return list(soup.find_all(target_tags, **kwargs))


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
