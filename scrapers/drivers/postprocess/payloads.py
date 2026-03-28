from __future__ import annotations

from dataclasses import dataclass

from scrapers.base.payloads import InfoboxPayload
from scrapers.base.payloads import SectionsPayload


@dataclass(frozen=True)
class DriverRecordPayload:
    infobox: InfoboxPayload
    career_results: SectionsPayload
