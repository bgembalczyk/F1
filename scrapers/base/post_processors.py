from collections.abc import Sequence
from typing import Protocol

from scrapers.base.logging import get_logger
from validation.validator_base import ExportRecord


class RecordPostProcessor(Protocol):
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]: ...


class CommonMetadataPostProcessor:
    """Compatibility post processor used by legacy tests."""

    def __init__(self, **metadata) -> None:
        self._metadata = {
            key: value.isoformat() if hasattr(value, "isoformat") else value
            for key, value in metadata.items()
        }

    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        if not self._metadata:
            return records
        enriched: list[ExportRecord] = []
        for record in records:
            merged = dict(record)
            merged.update(self._metadata)
            enriched.append(merged)
        return enriched


def apply_post_processors(
    post_processors: Sequence[RecordPostProcessor],
    records: list[ExportRecord],
    *,
    logger=None,
) -> list[ExportRecord]:
    resolved_logger = logger or get_logger("PostProcessorsPipeline")
    processed = list(records)
    for post_processor in post_processors:
        before_count = len(processed)
        resolved_logger.debug(
            "Post-processor %s: before=%d",
            post_processor.__class__.__name__,
            before_count,
        )
        processed = post_processor.post_process(processed)
        resolved_logger.debug(
            "Post-processor %s: after=%d",
            post_processor.__class__.__name__,
            len(processed),
        )
    return processed
