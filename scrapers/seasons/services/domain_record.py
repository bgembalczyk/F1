from __future__ import annotations

from typing import Any

from scrapers.base.postprocess import BaseRecordAssemblerInput
from scrapers.seasons.postprocess.assembler import SeasonPayloadDTO
from scrapers.seasons.postprocess.assembler import SeasonRecordAssembler
from scrapers.seasons.postprocess.assembler import SeasonRecordSections


class DomainRecordService:
    def __init__(self, *, assembler: SeasonRecordAssembler | None = None) -> None:
        self._assembler = assembler or SeasonRecordAssembler()

    def build_payload(
        self,
        payload: SeasonPayloadDTO | Any,
    ) -> SeasonPayloadDTO:
        if isinstance(payload, SeasonPayloadDTO):
            return payload
        return SeasonPayloadDTO(sections=SeasonRecordSections.empty())

    def build_sections_payload(
        self,
        payload: SeasonPayloadDTO | Any,
    ) -> SeasonRecordSections:
        return self.build_payload(payload).sections

    def assemble_record(
        self,
        payload: SeasonPayloadDTO | SeasonRecordSections,
    ) -> dict[str, Any]:
        if isinstance(payload, SeasonRecordSections):
            payload = SeasonPayloadDTO(
                sections=payload,
                base=BaseRecordAssemblerInput(),
            )
        return self._assembler.assemble(payload)
