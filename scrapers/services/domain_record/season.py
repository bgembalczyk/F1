from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from scrapers.base.postprocess.assembler import BaseRecordAssemblerInput
from scrapers.seasons.postprocess_seasons.assembler import SeasonPayloadDTO
from scrapers.seasons.postprocess_seasons.assembler import SeasonRecordAssembler
from scrapers.seasons.postprocess_seasons.assembler import SeasonRecordSections
from scrapers.services.domain_record._shared import DomainRecordResult

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssemblerProtocol


@dataclass(frozen=True, slots=True)
class SeasonDomainRecordInput:
    payload: SeasonPayloadDTO | SeasonRecordSections


class DomainRecordService:
    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[SeasonRecordSections] | None = None,
    ) -> None:
        self._assembler = assembler or SeasonRecordAssembler()

    def execute(self, payload: SeasonDomainRecordInput) -> DomainRecordResult:
        normalized_payload = self._build_payload(payload.payload)
        return DomainRecordResult(record=self._assembler.assemble(normalized_payload))

    def _build_payload(
        self,
        payload: SeasonPayloadDTO | SeasonRecordSections,
    ) -> SeasonPayloadDTO:
        if isinstance(payload, SeasonPayloadDTO):
            return payload
        return SeasonPayloadDTO(
            sections=payload,
            base=BaseRecordAssemblerInput(),
        )
