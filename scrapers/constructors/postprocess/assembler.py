from __future__ import annotations

from typing import Any

from scrapers.base.payloads import InfoboxPayload
from scrapers.base.payloads import SectionsPayload
from scrapers.base.payloads import TablesPayload


class ConstructorRecordAssembler:
    def assemble(
        self,
        *,
        url: str,
        infoboxes: InfoboxPayload,
        tables: TablesPayload,
        sections: SectionsPayload,
    ) -> dict[str, Any]:
        return {
            "url": url,
            "infoboxes": infoboxes.to_export(),
            "tables": tables.to_export(),
            "sections": sections.to_export(),
        }
