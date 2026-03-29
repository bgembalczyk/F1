from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from scrapers.base.logging import get_logger
from validation.validator_base import ExportRecord


class RecordPostProcessor(Protocol):
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]: ...


class CommonMetadataPostProcessor:
    def __init__(
        self,
        *,
        source_url: str,
        section_id: str | None,
        scraped_at: datetime,
    ) -> None:
        self._source_url = source_url
        self._section_id = section_id
        self._scraped_at = scraped_at

    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        enriched: list[ExportRecord] = []
        for record in records:
            payload = dict(record)
            payload.setdefault("source_url", self._source_url)
            payload.setdefault("section_id", self._section_id)
            payload.setdefault("scraped_at", self._scraped_at.isoformat())
            enriched.append(payload)
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
