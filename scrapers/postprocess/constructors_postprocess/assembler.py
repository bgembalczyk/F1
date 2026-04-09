from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.postprocess.assembler import BaseRecordAssembler
from scrapers.base.postprocess.assembler import BaseRecordAssemblerInput

if TYPE_CHECKING:
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
    metadata: dict[str, Any] | None = None


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
