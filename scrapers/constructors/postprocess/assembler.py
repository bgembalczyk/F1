from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from models.records.schemas import ConstructorExportRecord
from models.records.schemas import serialize_for_json
from models.records.schemas import validate_model_contract
from models.value_objects import WikiUrl
from scrapers.base.mappers import InfoboxRecordMapper
from scrapers.base.mappers import SectionRecordMapper
from scrapers.base.mappers import TableRecordMapper

logger = logging.getLogger(__name__)


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
        model = ConstructorExportRecord(
            url=url.to_export(),
            infoboxes=self._infobox_mapper.map_many(payload.infoboxes),
            tables=self._table_mapper.map_many(payload.tables),
            sections=self._section_mapper.map_many(payload.sections),
        )
        validate_model_contract(model, logger=logger)
        return serialize_for_json(model)
