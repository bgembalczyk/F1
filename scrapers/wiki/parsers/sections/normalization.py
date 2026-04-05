from __future__ import annotations

from scrapers.base.helpers.text import clean_wiki_text


def normalize_section_text(value: str | None) -> str:
    """Normalizuje nagłówek sekcji wiki do porównań i dopasowań aliasów."""
    if value is None:
        raise ValueError("Section text cannot be None.")
    if not isinstance(value, str):
        raise TypeError(f"Section text must be a string, got {type(value).__name__}.")

    # 1) Wikipedia często używa "_" zamiast spacji (np. w identyfikatorach sekcji).
    with_spaces = value.replace("_", " ")
    # 2) Usuwamy mark-up wiki/artefakty parsera.
    cleaned = clean_wiki_text(with_spaces)
    # 3) Ujednolicamy wielkość liter i obcinamy białe znaki dla stabilnych porównań.
    return cleaned.lower().strip()
