from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.postprocess.assembler import BaseRecordAssemblerInput
from scrapers.services.domain_record.base import BaseDomainRecordService
from scrapers.seasons.postprocess_seasons.assembler import SeasonPayloadDTO
from scrapers.seasons.postprocess_seasons.assembler import SeasonRecordAssembler
from scrapers.seasons.postprocess_seasons.assembler import SeasonRecordSections

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssemblerProtocol


@dataclass(frozen=True, slots=True)
class SeasonDomainRecordInput:
    payload: SeasonPayloadDTO | SeasonRecordSections


class SeasonDomainRecordService(BaseDomainRecordService[SeasonDomainRecordInput]):
    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[SeasonRecordSections] | None = None,
    ) -> None:
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

    def assemble_record(self, payload: SeasonDomainRecordInput) -> dict[str, Any]:
        assembled_payload = payload.payload
        if isinstance(assembled_payload, SeasonRecordSections):
            assembled_payload = SeasonPayloadDTO(
                sections=assembled_payload,
                base=BaseRecordAssemblerInput(),
            )
        return self._assembler.assemble(assembled_payload)


class DomainRecordService(SeasonDomainRecordService):
    """Compatibility alias for legacy imports."""
