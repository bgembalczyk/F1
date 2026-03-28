from __future__ import annotations

from scrapers.wiki.parsers.sections.detection import normalize_section_text


def normalize_section_profile_key(value: str) -> str:
    return normalize_section_text(value)
