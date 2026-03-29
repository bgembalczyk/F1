from typing import Any

from scrapers.sponsorship_liveries.parsers.splitters.record.pipeline_record import (
    PipelineRecord,
)


class DeduplicateRecordStrategy:
    def __init__(self):
        self._seen: set[tuple[Any, ...]] = set()

    def reset(self) -> None:
        self._seen.clear()

    def apply(self, record: PipelineRecord) -> list[PipelineRecord]:
        fingerprint = self._fingerprint(record.payload)
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
