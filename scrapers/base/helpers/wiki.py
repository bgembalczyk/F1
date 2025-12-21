"""Wikipedia helper utilities used by scrapers."""

from __future__ import annotations

from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_text


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
