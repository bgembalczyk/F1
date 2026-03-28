from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from models.value_objects import WikiUrl
from scrapers.base.mappers import InfoboxRecordMapper
from scrapers.base.mappers import SectionRecordMapper
from scrapers.base.mappers import TableRecordMapper


@dataclass(frozen=True)
class ConstructorRecordDTO:
    url: WikiUrl | str
    infoboxes: list[dict[str, Any]]
    tables: list[dict[str, Any]]
    sections: list[dict[str, Any]]


class ConstructorRecordAssembler:
    def __init__(
        self,
        *,
        infobox_mapper: InfoboxRecordMapper | None = None,
        table_mapper: TableRecordMapper | None = None,
        section_mapper: SectionRecordMapper | None = None,
    ) -> None:
        self._infobox_mapper = infobox_mapper or InfoboxRecordMapper()
        self._table_mapper = table_mapper or TableRecordMapper()
        self._section_mapper = section_mapper or SectionRecordMapper()

    def assemble(
        self,
        *,
        payload: ConstructorRecordDTO,
    ) -> dict[str, Any]:
        url = WikiUrl.from_raw(payload.url)
        return {
            "url": url.to_export(),
            "infoboxes": self._infobox_mapper.map_many(payload.infoboxes),
            "tables": self._table_mapper.map_many(payload.tables),
            "sections": self._section_mapper.map_many(payload.sections),
        }
