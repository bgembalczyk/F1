"""Utilities for resolving detail page URLs from list records."""

from collections.abc import Iterable
from typing import Any
from typing import Protocol

from scrapers.base.helpers.wiki import is_wikipedia_redlink


class DetailUrlResolver(Protocol):
    """Resolver API used by complete extractors to locate detail URLs."""

    def resolve(self, record: dict[str, Any]) -> str | None:
        """Return a resolved detail URL for the record or ``None``."""


def validate_detail_url(url: Any) -> str | None:
    """Validate and normalize raw detail URL candidates in one place."""
    if not isinstance(url, str):
        return None

    normalized = url.strip()
    if not normalized:
        return None

    if is_wikipedia_redlink(normalized):
        return None

    return normalized


def _resolve_dotted_value(record: dict[str, Any], dotted_key: str) -> Any:
    current: Any = record
    for part in dotted_key.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def resolve_first_valid_detail_url(
    record: dict[str, Any],
    *,
    candidate_keys: Iterable[str],
) -> str | None:
    """Resolve first valid URL from candidate keys (supports dotted paths)."""
    for key in candidate_keys:
        candidate = _resolve_dotted_value(record, key)
        validated = validate_detail_url(candidate)
        if validated:
            return validated
    return None

