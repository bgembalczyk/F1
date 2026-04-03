from __future__ import annotations

from collections.abc import Callable


def expand_alias_variants(
    values: set[str],
    *,
    text_normalizer: Callable[[str], str],
) -> tuple[set[str], set[str]]:
    """Build normalized text and id variants for alias matching."""
    normalized_texts = {
        text_normalizer(value)
        for value in values
        if isinstance(value, str) and value.strip()
    }
    normalized_ids = {
        variant
        for text in normalized_texts
        for variant in (text.replace(" ", "_"), text)
    }
    return normalized_ids, normalized_texts
