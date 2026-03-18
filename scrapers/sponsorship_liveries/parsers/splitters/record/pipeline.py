from __future__ import annotations

from typing import Any

from scrapers.sponsorship_liveries.parsers.splitters.record.protocols import (
    RecordSplitStrategy,
)


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
