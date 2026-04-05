from __future__ import annotations

from scrapers.base.helpers.text import clean_wiki_text


def normalize_section_text(value: str) -> str:
    text = clean_wiki_text(value.replace("_", " "))
    return text.lower().strip()
