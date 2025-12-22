"""Wikipedia helper utilities used by scrapers."""

from __future__ import annotations

from bs4 import Tag

from models.records import LinkRecord
from scrapers.base.helpers.text_normalization import clean_text, is_language_link


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
        text = clean_text(tag.get_text(strip=True))
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
    Sprawdza czy link jest markerem językowym (np. '(it)' z linkiem do it.wikipedia.org).

    Args:
        text: Tekst linku (np. 'it', 'de', 'es')
        url: URL linku

    Returns:
        True jeśli to marker językowy do odfiltrowania
    """
    if not text or not url:
        return False

    # Typowe 2-3 znakowe kody języków
    text_clean = text.strip().lower()
    if len(text_clean) not in (2, 3):
        return False

    # Sprawdź czy URL prowadzi do innej wersji językowej Wikipedii
    # np. https://it.wikipedia.org/, https://de.wikipedia.org/
    url_lower = url.lower()
    if "wikipedia.org" in url_lower:
        # Wzorzec: {kod}.wikipedia.org
        if f"{text_clean}.wikipedia.org" in url_lower:
            return True
        # Wzorzec: wikipedia.org/{kod}/
        if f"wikipedia.org/{text_clean}/" in url_lower:
            return True

    return False


def clean_link_record(link: LinkRecord) -> LinkRecord | None:
    """
    Ujednolica linki:
    - usuwa markery językowe (logika z is_language_link i is_language_marker_link),
    - zamienia redlink na url=None,
    - zwraca None dla pustego tekstu.
    """
    link_text = clean_text(link.get("text") or "")
    if not link_text:
        return None

    url = link.get("url")

    if is_language_link(link_text, url) or is_language_marker_link(link_text, url):
        return None

    if is_wikipedia_redlink(url):
        url = None

    return {"text": link_text, "url": url}
