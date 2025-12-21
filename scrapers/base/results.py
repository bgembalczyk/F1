from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from scrapers.base.records import ExportRecord


@dataclass(frozen=True)
class ScrapeResult:
    data: List[ExportRecord]
    source_url: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
