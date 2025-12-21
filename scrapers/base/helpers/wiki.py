"""Wikipedia/HTML helper utilities used by scrapers."""

from __future__ import annotations

from typing import Any, Callable, Iterable

from bs4 import BeautifulSoup, Tag

from models.records import LinkRecord
from scrapers.base.helpers.text_normalization import clean_text, is_language_link

# ============================================================================
# Text Normalization
# ============================================================================


def clean_wiki_text(text: str) -> str:
    """Normalizuje whitespace i usuwa przypisy Wikipedii."""
    return clean_text(text)


def strip_marks(text: str | None) -> str | None:
    """Usuwa typowe znaki oznaczeń z tabel."""
    if text is None:
        return None
    return (
        text.replace("*", "")
        .replace("†", "")
        .replace("‡", "")
        .replace("✝", "")
        .replace("✚", "")
        .replace("~", "")
        .replace("^", "")
        .strip()
    )


# ============================================================================
# Section & Element Finding
# ============================================================================


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


# ============================================================================
# Link Extraction & Validation
# ============================================================================


def extract_links_from_cell(
    cell: Tag,
    *,
    full_url: Callable[[str | None], str | None],
) -> list[LinkRecord]:
    """
    Zwraca listę linków {text, url} z komórki,
    ignorując przypisy (cite_note / reference).
    """
    links: list[LinkRecord] = []

    for a in cell.find_all("a", href=True):
        href = a.get("href") or ""
        text = clean_wiki_text(a.get_text(strip=True))

        if is_reference_link(a, allow_local_anchors=True):
            continue

        url = full_url(href)
        if is_wikipedia_redlink(url):
            url = None

        if is_language_link(text, url):
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
        text = clean_wiki_text(tag.get_text(strip=True))
        return not text or not allow_local_anchors

    return False


def is_wikipedia_redlink(url: str | None) -> bool:
    """Return True for Wikipedia redlinks like ...&action=edit&redlink=1."""
    if not url:
        return False

    url_l = url.lower()
    return "wikipedia.org" in url_l and "action=edit" in url_l and "redlink=" in url_l

