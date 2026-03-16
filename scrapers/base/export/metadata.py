from dataclasses import dataclass
from datetime import datetime
from typing import Any

from scrapers.base.results import ScrapeResult


@dataclass(frozen=True)
class ExportMetadata:
    source_url: str | None
    scraped_at: datetime
    parser_version: str | None
    schema_version: str | None
    records_count: int

    @classmethod
    def from_result(cls, result: ScrapeResult) -> "ExportMetadata":
        return cls(
            source_url=result.source_url,
            scraped_at=result.timestamp,
            parser_version=result.parser_version,
            schema_version=result.schema_version,
            records_count=len(result.data),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_url": self.source_url,
            "scraped_at": self.scraped_at.isoformat(),
            "parser_version": self.parser_version,
            "schema_version": self.schema_version,
            "records_count": self.records_count,
        }
