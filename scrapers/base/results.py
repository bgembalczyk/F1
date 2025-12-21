from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from scrapers.base.types import ExportableRecord


@dataclass(frozen=True)
class ScrapeResult:
    data: list[ExportableRecord]
    source_url: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
