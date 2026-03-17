from __future__ import annotations

from typing import Any

from scrapers.sponsorship_liveries.parsers.record_splitter_protocols import (
    RecordSplitStrategy,
)


class DeduplicateRecordStrategy:
    def __init__(self):
        self._seen: set[tuple[Any, ...]] = set()

    def reset(self) -> None:
        self._seen.clear()

    def apply(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        fingerprint = self._fingerprint(record)
        if fingerprint in self._seen:
            return []
        self._seen.add(fingerprint)
        return [record]

    @staticmethod
    def _fingerprint(value: Any) -> tuple[Any, ...]:
        if isinstance(value, dict):
            return (
                "dict",
                tuple(
                    (key, DeduplicateRecordStrategy._fingerprint(val))
                    for key, val in sorted(value.items())
                ),
            )
        if isinstance(value, list):
            return (
                "list",
                tuple(DeduplicateRecordStrategy._fingerprint(item) for item in value),
            )
        return ("scalar", str(value))


class RecordSplitPipeline:
    def __init__(self, strategies: list[RecordSplitStrategy]):
        self._strategies = strategies

    def apply(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        for strategy in self._strategies:
            if hasattr(strategy, "reset"):
                strategy.reset()  # type: ignore[attr-defined]

        records = [record]
        for strategy in self._strategies:
            next_records: list[dict[str, Any]] = []
            for candidate in records:
                next_records.extend(strategy.apply(candidate))
            records = next_records
        return records
