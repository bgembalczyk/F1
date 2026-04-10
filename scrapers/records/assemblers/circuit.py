from __future__ import annotations

from typing import Any

from scrapers.records.assemblers.base import BaseRecordAssembler
from scrapers.records.assemblers.base import BaseRecordAssemblerInput
from scrapers.records.dto.circuit import CircuitRecordDTO
from scrapers.records.mappers.infobox import InfoboxRecordMapper
from scrapers.records.mappers.section import SectionRecordMapper
from scrapers.records.mappers.table_record.layout import LayoutTableRecordMapper


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
        payload: CircuitRecordDTO,
    ) -> dict[str, Any]:
        record = super().assemble(
            BaseRecordAssemblerInput(
                url=payload.url,
                metadata=payload.metadata,
                infobox=payload.infobox,
                sections=payload.sections,
            ),
        )
        record["tables"] = self._layout_table_mapper.map(payload.lap_record_rows)
        return record
