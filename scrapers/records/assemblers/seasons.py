from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from typing import Any

from scrapers.records.dto.season import SeasonPayloadDTO
from scrapers.records.assemblers.base import BaseRecordAssembler
from scrapers.records.sections.season import SeasonRecordSections


class SeasonRecordAssembler(BaseRecordAssembler):
    def assemble(
        self,
        payload: SeasonPayloadDTO | SeasonRecordSections,
    ) -> dict[str, Any]:
        dto = (
            payload
            if isinstance(payload, SeasonPayloadDTO)
            else SeasonPayloadDTO(sections=payload)
        )
        record = super().assemble(dto.base)
        record.update(self._map_sections(dto.sections))
        return record

    def _map_sections(self, sections: SeasonRecordSections) -> dict[str, Any]:
        return {
            section_field.name: getattr(sections, section_field.name)
            for section_field in fields(SeasonRecordSections)
        }
