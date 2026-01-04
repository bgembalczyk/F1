"""Wikipedia helper utilities used by scrapers."""

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text_normalization import is_language_link
from scrapers.base.helpers.url import normalize_url


def build_full_url(base: str, href: str) -> str | None:
    """
    Buduje pełny URL na podstawie bazy i href.

    Obsługuje przypadki:
    - względne ścieżki (/wiki/...),
    - schemowe URL-e (//...),
    - absolutne URL-e (http/https i inne schematy).
    """
    return normalize_url(base, href)


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


def clean_link_record(link: LinkRecord) -> LinkRecord | None:
    """
    Ujednolica linki:
    - usuwa markery językowe (logika z is_language_link),
    - zamienia redlink na url=None,
    - zwraca None dla pustego tekstu.
    """
    link_text = clean_wiki_text(link.get("text") or "")
    if not link_text:
        return None

    url = link.get("url")

    if is_language_link(link_text, url):
        return None

    if is_wikipedia_redlink(url):
        url = None

    return {"text": link_text, "url": url}
