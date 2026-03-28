from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from models.value_objects import WikiUrl
from scrapers.base.mappers import InfoboxRecordMapper
from scrapers.base.mappers import LayoutTableRecordMapper
from scrapers.base.mappers import SectionRecordMapper
from scrapers.base.postprocess import BaseRecordAssembler
from scrapers.base.postprocess import BaseRecordAssemblerInput


@dataclass(frozen=True)
class CircuitRecordDTO:
    url: WikiUrl | str
    infobox: dict[str, Any]
    lap_record_rows: list[dict[str, Any]]
    sections: list[dict[str, Any]]
    metadata: dict[str, Any] | None = None


class CircuitRecordAssembler(BaseRecordAssembler):
    def __init__(
        self,
        *,
        infobox_mapper: InfoboxRecordMapper | None = None,
        section_mapper: SectionRecordMapper | None = None,
        table_mapper: LayoutTableRecordMapper | None = None,
    ) -> None:
        super().__init__(
            infobox_mapper=infobox_mapper,
            table_mapper=None,
            section_mapper=section_mapper,
        )
        self._layout_table_mapper = table_mapper or LayoutTableRecordMapper()

    def assemble(
        self,
        *,
        payload: CircuitRecordDTO,
    ) -> dict[str, Any]:
        record = super().assemble(
            payload=BaseRecordAssemblerInput(
                url=payload.url,
                metadata=payload.metadata,
                infobox=payload.infobox,
                sections=payload.sections,
            ),
        )
        record["tables"] = self._layout_table_mapper.map(payload.lap_record_rows)
        return record
