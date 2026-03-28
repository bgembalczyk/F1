from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from models.value_objects import WikiUrl
from scrapers.base.mappers import InfoboxRecordMapper
from scrapers.base.mappers import LayoutTableRecordMapper
from scrapers.base.mappers import SectionRecordMapper


@dataclass(frozen=True)
class CircuitRecordDTO:
    url: WikiUrl | str
    infobox: dict[str, Any]
    lap_record_rows: list[dict[str, Any]]
    sections: list[dict[str, Any]]


class CircuitRecordAssembler:
    def __init__(
        self,
        *,
        infobox_mapper: InfoboxRecordMapper | None = None,
        section_mapper: SectionRecordMapper | None = None,
        table_mapper: LayoutTableRecordMapper | None = None,
    ) -> None:
        self._infobox_mapper = infobox_mapper or InfoboxRecordMapper()
        self._section_mapper = section_mapper or SectionRecordMapper()
        self._table_mapper = table_mapper or LayoutTableRecordMapper()

    def assemble(
        self,
        *,
        payload: CircuitRecordDTO,
    ) -> dict[str, Any]:
        url = WikiUrl.from_raw(payload.url)
        return {
            "url": url.to_export(),
            "infobox": self._infobox_mapper.map(payload.infobox),
            "tables": self._table_mapper.map(payload.lap_record_rows),
            "sections": self._section_mapper.map_many(payload.sections),
        }
