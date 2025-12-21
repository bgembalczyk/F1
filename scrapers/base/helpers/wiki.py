"""Wikipedia/HTML helper utilities used by scrapers."""

from __future__ import annotations

import re
from typing import Any, Callable, Iterable
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.text import clean_wiki_text

__all__ = [
    "extract_links_from_cell",
    "find_section_elements",
    "is_language_marker_link",
    "is_reference_link",
    "is_wikipedia_redlink",
]


def find_section_elements(
    soup: BeautifulSoup,
    section_id: str | None,
    target_tags: Iterable[str],
    **kwargs: Any,
) -> list[Tag]:
    """Find elements after a section heading or across the whole document."""
    if section_id:
        heading = soup.find(id=section_id)
        if not heading:
            raise RuntimeError(f"Nie znaleziono sekcji o id={section_id!r}")

        return list(heading.find_all_next(target_tags, **kwargs))

    return list(soup.find_all(target_tags, **kwargs))


def extract_links_from_cell(
    cell: Tag,
    *,
    full_url: Callable[[str | None], str | None],
) -> list[dict[str, Any]]:
    """
    Zwraca listę linków {text, url} z komórki,
    ignorując przypisy (cite_note / reference).
    """
    links: list[dict[str, Any]] = []

    for a in cell.find_all("a", href=True):
        href = a.get("href") or ""
        text = clean_wiki_text(a.get_text(strip=True))

        if is_reference_link(a, allow_local_anchors=True):
            continue

        url = full_url(href)
        if is_wikipedia_redlink(url):
            url = None

        if is_language_marker_link(text, url):
            continue

        links.append({"text": text, "url": url})

    return links


def is_reference_link(tag: Tag, *, allow_local_anchors: bool = False) -> bool:
    """
    Sprawdza, czy ``<a>`` powinno być traktowane jako przypis/odnośnik techniczny.

    Kryteria:
    - ``href`` zawiera ``cite_note``;
    - klasa ``reference`` lub ``mw-cite-backlink``;
    - lokalne kotwice (``href`` zaczynające się od ``#``):
      - zawsze ignorowane gdy ``allow_local_anchors`` jest False;
      - ignorowane gdy tekst jest pusty nawet przy ``allow_local_anchors=True``.
    """
    href = tag.get("href") or ""
    classes = tag.get("class") or []

    if any(cls in ("reference", "mw-cite-backlink") for cls in classes):
        return True

    if "cite_note" in href:
        return True

    if href.startswith("#"):
        text = clean_wiki_text(tag.get_text(" ", strip=True))
        return not text or not allow_local_anchors

    return False


def is_wikipedia_redlink(url: str | None) -> bool:
    """Return True for Wikipedia redlinks like ...&action=edit&redlink=1."""
    if not url:
        return False

    url_l = url.lower()
    return "wikipedia.org" in url_l and "action=edit" in url_l and "redlink=" in url_l


def is_language_marker_link(text: str | None, url: str | None) -> bool:
    """
    True tylko dla interwiki markerów typu:
    text='fr' i url='https://fr.wikipedia.org/wiki/...'
    """
    if not text or not url:
        return False

    txt = text.strip().lower()
    if not (2 <= len(txt) <= 3) or not txt.isalpha():
        return False

    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return False

    m = re.match(r"^([a-z]{2,3})\.(m\.)?wikipedia\.org$", host)
    if not m:
        return False

    lang = m.group(1)
    return txt == lang
