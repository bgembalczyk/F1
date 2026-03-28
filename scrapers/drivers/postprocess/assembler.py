from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from models.records.schemas import DriverExportRecord
from models.records.schemas import serialize_for_json
from models.records.schemas import validate_model_contract
from models.value_objects import WikiUrl
from scrapers.base.mappers import InfoboxRecordMapper
from scrapers.base.mappers import SectionRecordMapper

logger = logging.getLogger(__name__)


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
        section_mapper: SectionRecordMapper | None = None,
    ) -> None:
        self._infobox_mapper = infobox_mapper or InfoboxRecordMapper()
        self._section_mapper = section_mapper or SectionRecordMapper()

    def assemble(
        self,
        *,
        payload: DriverRecordDTO,
    ) -> dict[str, Any]:
        url = WikiUrl.from_raw(payload.url)
        model = DriverExportRecord(
            url=url.to_export(),
            infobox=self._infobox_mapper.map(payload.infobox),
            career_results=self._section_mapper.map_many(payload.career_results),
        )
        validate_model_contract(model, logger=logger)
        return serialize_for_json(model)
