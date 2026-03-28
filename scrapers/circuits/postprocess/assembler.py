from __future__ import annotations

from typing import Any

from scrapers.base.payloads import InfoboxPayload
from scrapers.base.payloads import SectionsPayload
from scrapers.circuits.postprocess.payloads import CircuitTablesPayload


class CircuitRecordAssembler:
    def assemble(
        self,
        *,
        url: str,
        infobox: InfoboxPayload,
        tables: CircuitTablesPayload,
        sections: SectionsPayload,
    ) -> dict[str, Any]:
        return {
            "url": url,
            "infobox": infobox.to_export(),
            "tables": tables.to_export(),
            "sections": sections.to_export(),
        }
