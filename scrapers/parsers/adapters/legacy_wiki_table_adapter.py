from __future__ import annotations

from typing import Any

from scrapers.parsers.table.wiki.base import WikiTablePayloadCollector
from scrapers.parsers.table.wiki.base import WikiTablePayloadTransformer


class LegacyParseGroupAdapter:
    """Backward-compatible adapter for call-sites still invoking `parse_group`."""

    def __init__(self, collector: WikiTablePayloadCollector) -> None:
        self._collector = collector

    def parse_group(self, payload: Any) -> list[dict[str, Any]]:
        return self._collector.collect(payload)

    collect_rows = parse_group


class LegacyApplyToPayloadAdapter:
    """Backward-compatible adapter for call-sites still invoking `apply_to_payload`."""

    def __init__(self, transformer: WikiTablePayloadTransformer) -> None:
        self._transformer = transformer

    def apply_to_payload(self, payload: dict[str, Any]) -> None:
        self._transformer.transform(payload)


__all__ = ["LegacyApplyToPayloadAdapter", "LegacyParseGroupAdapter"]
