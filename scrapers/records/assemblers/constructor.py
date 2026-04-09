from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from scrapers.records.DTO.constructor import ConstructorRecordDTO
from scrapers.records.assemblers.base import BaseRecordAssembler
from scrapers.records.assemblers.base import BaseRecordAssemblerInput
from scrapers.records.infobox_record import InfoboxRecordMapper
from scrapers.records.section_record import SectionRecordMapper
from scrapers.records.table_record.base import TableRecordMapper

if TYPE_CHECKING:
    from models.value_objects import WikiUrl



class ConstructorRecordAssembler(BaseRecordAssembler):
    def __init__(
        self,
        *,
        infobox_mapper: InfoboxRecordMapper | None = None,
        table_mapper: TableRecordMapper | None = None,
        section_mapper: SectionRecordMapper | None = None,
    ) -> None:
        super().__init__(
            infobox_mapper=infobox_mapper,
            table_mapper=table_mapper,
            section_mapper=section_mapper,
        )

    def assemble(
        self,
        payload: ConstructorRecordDTO,
    ) -> dict[str, Any]:
        return super().assemble(
            BaseRecordAssemblerInput(
                url=payload.url,
                metadata=payload.metadata,
                infoboxes=payload.infoboxes,
                tables=payload.tables,
                sections=payload.sections,
            ),
        )
