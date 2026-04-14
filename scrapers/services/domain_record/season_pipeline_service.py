from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.records.assemblers.seasons import SeasonRecordAssembler
from scrapers.records.dto.season import SeasonPayloadDTO
from scrapers.records.inputs.base_assembler import BaseRecordAssemblerInput
from scrapers.records.sections.season import SeasonRecordSections
from scrapers.services.domain_record.base import DomainPipelineService


@dataclass(frozen=True, slots=True)
class SeasonDomainRecordInput:
    payload: SeasonPayloadDTO | SeasonRecordSections | Any


class SeasonPipelineService(
    DomainPipelineService[SeasonDomainRecordInput, SeasonPayloadDTO, dict[str, Any]],
):
    def __init__(
        self,
        *,
        assembler: Any | None = None,
    ) -> None:
        self._assembler = assembler or SeasonRecordAssembler()

    def build_payload(self, input_dto: SeasonDomainRecordInput) -> SeasonPayloadDTO:
        payload = input_dto.payload
        if isinstance(payload, SeasonPayloadDTO):
            return payload
        if isinstance(payload, SeasonRecordSections):
            return SeasonPayloadDTO(sections=payload, base=BaseRecordAssemblerInput())
        return SeasonPayloadDTO(sections=SeasonRecordSections.empty())

    def build_sections_payload(
        self,
        payload: SeasonPayloadDTO | SeasonRecordSections | Any,
    ) -> SeasonRecordSections:
        return self.build_payload(SeasonDomainRecordInput(payload=payload)).sections

    def assemble(self, payload: SeasonPayloadDTO) -> dict[str, Any]:
        return self._assembler.assemble(payload)

    def _compat_input_from_source(
        self,
        source: dict[str, Any],
    ) -> SeasonDomainRecordInput:
        return SeasonDomainRecordInput(payload=source.get("payload"))

