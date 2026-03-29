from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone

from validation.validator_base import ExportRecord


@dataclass(frozen=True)
class ScrapeResult:
    data: list[ExportRecord]
    source_url: str | None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
