from __future__ import annotations

from dataclasses import dataclass

from scrapers.base.payloads import InfoboxPayload
from scrapers.base.payloads import SectionsPayload
from scrapers.base.payloads import TablesPayload


@dataclass(frozen=True)
class ConstructorRecordPayload:
    infoboxes: InfoboxPayload
    tables: TablesPayload
    sections: SectionsPayload
