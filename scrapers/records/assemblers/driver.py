from __future__ import annotations

from typing import Any

from models.wiki_url import WikiUrl
from scrapers.records.assemblers.base import BaseRecordAssembler
from scrapers.records.dto.driver import DriverRecordDTO
from scrapers.records.mappers.infobox import InfoboxRecordMapper


class DriverRecordAssembler(BaseRecordAssembler):
    def __init__(
        self,
        *,
        infobox_mapper: InfoboxRecordMapper | None = None,
    ) -> None:
        super().__init__(
            infobox_mapper=infobox_mapper,
        )

    def assemble(
        self,
        payload: DriverRecordDTO,
    ) -> dict[str, Any]:
        url = WikiUrl.from_raw(payload.url)
        return {
            "url": url.to_export(),
            "infobox": self._infobox_mapper.map(payload.infobox),
            "career_results": payload.career_results,
        }
