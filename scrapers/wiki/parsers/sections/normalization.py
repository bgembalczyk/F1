from __future__ import annotations

from scrapers.base.helpers.text import clean_wiki_text


def normalize_section_text(value: str) -> str:
    normalized_value = value.replace("_", " ")
    cleaned_text = clean_wiki_text(normalized_value)
    return cleaned_text.lower().strip()
