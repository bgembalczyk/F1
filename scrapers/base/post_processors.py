from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from scrapers.base.logging import get_logger
from validation.validator_base import ExportRecord


class RecordPostProcessor(Protocol):
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]: ...


@dataclass(frozen=True)
class CommonMetadataPostProcessor:
    source_url: str
    section_id: str | None = None
    scraped_at: datetime | None = None

    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        result: list[ExportRecord] = []
        for record in records:
            payload = dict(record)
            payload["source_url"] = self.source_url
            if self.section_id is not None:
                payload["section_id"] = self.section_id
            if self.scraped_at is not None:
                payload["scraped_at"] = self.scraped_at.isoformat()
            result.append(payload)
        return result


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
