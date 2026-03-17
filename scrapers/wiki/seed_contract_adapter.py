from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Any

from models.contracts.seed import SeedRecord


@dataclass(frozen=True)
class SeedRecordContractAdapter:
    """Wspólny adapter walidacji/normalizacji rekordów dla layer-0 list scrapers."""

    def adapt(
        self,
        *,
        records: list[dict[str, Any]],
        source_url: str,
        scraped_at: datetime | None = None,
    ) -> list[dict[str, Any]]:
        timestamp = scraped_at or datetime.now(tz=timezone.utc)
        return [
            SeedRecord.from_raw(
                record,
                source_url=source_url,
                scraped_at=timestamp,
            ).to_dict()
            for record in records
        ]
