from __future__ import annotations

from typing import Any

from models.wiki_url import WikiUrl
from scrapers.records.assemblers.base import BaseRecordAssembler
from scrapers.records.dto.driver import DriverRecordDTO
from scrapers.records.mappers.infobox import InfoboxRecordMapper
from scrapers.records.mappers.table_record.base import TableRecordMapper


class DriverRecordAssembler(BaseRecordAssembler):
    def __init__(
        self,
        *,
        infobox_mapper: InfoboxRecordMapper | None = None,
        record_mapper: TableRecordMapper | None = None,
    ) -> None:
        super().__init__(
            infobox_mapper=infobox_mapper,
            table_mapper=record_mapper,
        )

    def assemble(
        self,
        payload: DriverRecordDTO,
    ) -> dict[str, Any]:
        url = WikiUrl.from_raw(payload.url)
        return {
            "url": url.to_export(),
            "infobox": self._infobox_mapper.map(payload.infobox),
            "career_results": self._table_mapper.map_many(payload.career_results),
        }
