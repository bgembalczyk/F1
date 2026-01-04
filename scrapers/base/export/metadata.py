from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from scrapers.base.results import ScrapeResult


@dataclass(frozen=True)
class ExportMetadata:
    source_url: str | None
    timestamp: datetime
    records_count: int

    @classmethod
    def from_result(cls, result: ScrapeResult) -> "ExportMetadata":
        return cls(
            source_url=result.source_url,
            timestamp=result.timestamp,
            records_count=len(result.data),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_url": self.source_url,
            "timestamp": self.timestamp.isoformat(),
            "records_count": self.records_count,
        }
