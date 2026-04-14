from __future__ import annotations

from typing import Any

from scrapers.records.assemblers.base import BaseRecordAssembler
from scrapers.records.assemblers.base import BaseRecordAssemblerInput
from scrapers.records.dto.constructor import ConstructorRecordDTO
from scrapers.records.mappers.infobox import InfoboxRecordMapper
from scrapers.records.mappers.section import SectionRecordMapper


class ConstructorRecordAssembler(BaseRecordAssembler):
    def __init__(
        self,
        *,
        infobox_mapper: InfoboxRecordMapper | None = None,
        section_mapper: SectionRecordMapper | None = None,
    ) -> None:
        super().__init__(
            infobox_mapper=infobox_mapper,
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
