from __future__ import annotations

from scrapers.base.helpers.text import clean_wiki_text


def normalize_section_text(value: str) -> str:
    return clean_wiki_text(value.replace("_", " ")).lower().strip()
