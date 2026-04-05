from __future__ import annotations

from scrapers.base.helpers.text import clean_wiki_text


def normalize_section_text(value: str | None) -> str:
    """Normalizuje nagłówek sekcji wiki do porównań i dopasowań aliasów."""
    if value is None:
        msg = "Section text cannot be None."
        raise ValueError(msg)
    if not isinstance(value, str):
        msg = f"Section text must be a string, got {type(value).__name__}."
        raise TypeError(msg)

    # 1) Wikipedia często używa "_" zamiast spacji (np. w identyfikatorach sekcji).
    with_spaces = value.replace("_", " ")
    # 2) Usuwamy mark-up wiki/artefakty parsera.
    cleaned = clean_wiki_text(with_spaces)
    # 3) Ujednolicamy wielkość liter i obcinamy białe znaki dla stabilnych porównań.
    return cleaned.lower().strip()
