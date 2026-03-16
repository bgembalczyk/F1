from __future__ import annotations

from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text


def extract_text(element: Tag | None) -> str | None:
    """Extract normalized plain text from a tag."""
    if element is None:
        return None
    text = element.get_text(" ", strip=True)
    return text or None


def clean_table_cell_text(
    text: str,
    *,
    strip_lang_suffix: bool,
    strip_refs: bool,
    normalize_dashes: bool,
) -> str:
    """Apply canonical wiki text cleaning used by section/table parsers."""
    return clean_wiki_text(
        text,
        strip_lang_suffix=strip_lang_suffix,
        strip_refs=strip_refs,
        normalize_dashes=normalize_dashes,
    )
