from __future__ import annotations

from typing import Any

from scrapers.base.payloads import InfoboxPayload
from scrapers.base.payloads import SectionsPayload


class DriverRecordAssembler:
    def assemble(
        self,
        *,
        url: str,
        infobox: InfoboxPayload,
        career_results: SectionsPayload,
    ) -> dict[str, Any]:
        return {
            "url": url,
            "infobox": infobox.to_export(),
            "career_results": career_results.to_export(),
        }
