from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.postprocess.assembler import BaseRecordAssemblerInput
from scrapers.seasons.postprocess_seasons.assembler import SeasonPayloadDTO
from scrapers.seasons.postprocess_seasons.assembler import SeasonRecordAssembler
from scrapers.seasons.postprocess_seasons.assembler import SeasonRecordSections
from scrapers.services.domain_record.base_pipeline_service import BaseAssemblerPipelineService

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssemblerProtocol


@dataclass(frozen=True, slots=True)
class SeasonDomainRecordInput:
    payload: SeasonPayloadDTO | SeasonRecordSections


class SeasonPipelineService(
    BaseAssemblerPipelineService[SeasonDomainRecordInput, SeasonPayloadDTO],
):
    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[SeasonRecordSections] | None = None,
    ) -> None:
        self._assembler = assembler or SeasonRecordAssembler()

    def build_payload(self, input_dto: SeasonDomainRecordInput) -> SeasonPayloadDTO:
        payload = input_dto.payload
        if isinstance(payload, SeasonRecordSections):
            return SeasonPayloadDTO(sections=payload, base=BaseRecordAssemblerInput())
        if isinstance(payload, SeasonPayloadDTO):
            return payload
        return SeasonPayloadDTO(sections=SeasonRecordSections.empty())

    def build_sections_payload(self, payload: SeasonPayloadDTO | Any) -> SeasonRecordSections:
        if isinstance(payload, SeasonPayloadDTO):
            return payload.sections
        return self.build_payload(SeasonDomainRecordInput(payload=payload)).sections

    def assemble(self, payload: SeasonPayloadDTO) -> dict[str, Any]:
        return self._assembler.assemble(payload)

    def _compat_input_from_source(self, source: dict[str, Any]) -> SeasonDomainRecordInput:
        return SeasonDomainRecordInput(payload=source.get("payload"))
