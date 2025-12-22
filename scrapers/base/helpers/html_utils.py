"""HTML helper utilities used by scrapers."""

from __future__ import annotations

from typing import Any, Callable, Iterable

from bs4 import BeautifulSoup, Tag

from models.records import LinkRecord
from scrapers.base.helpers.text_normalization import clean_wiki_text as base_clean_wiki_text
from scrapers.base.helpers.wiki import clean_link_record, is_reference_link


def clean_wiki_text(text: str) -> str:
    """Normalizuje whitespace i usuwa przypisy Wikipedii."""
    return base_clean_wiki_text(text)


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
            raise RuntimeError(f"Nie znaleziono sekcji o id={section_id!r}")

        return list(heading.find_all_next(target_tags, **kwargs))

    return list(soup.find_all(target_tags, **kwargs))


def extract_links_from_cell(
    cell: Tag,
    *,
    full_url: Callable[[str], str] | None = None,
    allow_local_anchors: bool = True,
) -> list[LinkRecord]:
    """
    Zwraca listę linków {text, url} z komórki,
    ignorując przypisy (cite_note / reference).
    """
    links: list[LinkRecord] = []

    for a in cell.find_all("a", href=True):
        href = str(a.get("href") or "")
        text = clean_wiki_text(a.get_text(strip=True))

        if is_reference_link(a, allow_local_anchors=allow_local_anchors):
            continue

        url: str | None = full_url(href) if full_url else href
        link: LinkRecord = {"text": text, "url": url}
        cleaned = clean_link_record(link)
        if cleaned:
            links.append(cleaned)

    return links
