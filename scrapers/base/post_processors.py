from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from scrapers.base.logging import get_logger
from validation.validator_base import ExportRecord


class RecordPostProcessor(Protocol):
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]: ...


class CommonMetadataPostProcessor:
    """Unifies shared metadata keys across domain outputs.

    Standard keys:
    - source_url
    - section_id
    - scraped_at
    """

    def __init__(
        self,
        *,
        source_url: str,
        section_id: str,
        scraped_at: datetime | str,
    ) -> None:
        self.source_url = source_url
        self.section_id = section_id
        self.scraped_at = (
            scraped_at.isoformat() if isinstance(scraped_at, datetime) else scraped_at
        )

    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        normalized: list[ExportRecord] = []
        for record in records:
            item = dict(record)
            source_url = item.get("source_url") or item.get("url") or self.source_url
            section_id = (
                item.get("section_id")
                or item.get("source_section_id")
                or self.section_id
            )
            scraped_at = item.get("scraped_at") or self.scraped_at

            item["source_url"] = source_url
            item["section_id"] = section_id
            item["scraped_at"] = scraped_at
            normalized.append(item)

        return normalized


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
