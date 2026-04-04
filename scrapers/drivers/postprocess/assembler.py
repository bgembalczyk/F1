from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from models.value_objects import WikiUrl
from scrapers.base.mappers.infobox_record import InfoboxRecordMapper
from scrapers.base.mappers.table_record import TableRecordMapper


@dataclass(frozen=True)
class DriverRecordDTO:
    url: WikiUrl | str
    infobox: dict[str, Any]
    career_results: list[dict[str, Any]]


class DriverRecordAssembler:
    def __init__(
        self,
        *,
        infobox_mapper: InfoboxRecordMapper | None = None,
        record_mapper: TableRecordMapper | None = None,
    ) -> None:
        self._infobox_mapper = infobox_mapper or InfoboxRecordMapper()
        self._record_mapper = record_mapper or TableRecordMapper()

    def assemble(
        self,
        payload: DriverRecordDTO,
    ) -> dict[str, Any]:
        url = WikiUrl.from_raw(payload.url)
        return {
            "url": url.to_export(),
            "infobox": self._infobox_mapper.map(payload.infobox),
            "career_results": self._record_mapper.map_many(payload.career_results),
        }
