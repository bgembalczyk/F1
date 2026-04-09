from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from models.wiki_url import WikiUrl
from scrapers.records.infobox_record import InfoboxRecordMapper
from scrapers.records.inputs.base_assembler import BaseRecordAssemblerInput
from scrapers.records.section_record import SectionRecordMapper
from scrapers.records.table_record.base import TableRecordMapper

if TYPE_CHECKING:
    from collections.abc import Mapping




class BaseRecordAssembler:
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

    def assemble(self, payload: BaseRecordAssemblerInput) -> dict[str, Any]:
        record: dict[str, Any] = {}
        if payload.url is not None:
            record["url"] = WikiUrl.from_raw(payload.url).to_export()
        if payload.metadata is not None:
            record["metadata"] = dict(payload.metadata)
        if payload.infobox is not None:
            record["infobox"] = self._infobox_mapper.map(payload.infobox)
        if payload.infoboxes is not None:
            record["infoboxes"] = self._infobox_mapper.map_many(payload.infoboxes)
        if payload.tables is not None:
            record["tables"] = self._table_mapper.map_many(payload.tables)
        if payload.sections is not None:
            record["sections"] = self._section_mapper.map_many(payload.sections)
        return record
