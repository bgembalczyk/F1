from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from scrapers.records.assemblers.circuit import CircuitRecordAssembler
from scrapers.records.dto.circuit import CircuitRecordDTO
from scrapers.services.domain_record.base_pipeline_service import (
    BaseDomainPipelineService,
)

if TYPE_CHECKING:
    from scrapers.contracts import RecordAssemblerProtocol


@dataclass(frozen=True, slots=True)
class CircuitDomainRecordInput:
    source_url: str
    infobox: dict[str, Any]
    lap_record_rows: list[dict[str, Any]]
    sections: list[dict[str, Any]]


class CircuitPipelineService(
    BaseDomainPipelineService[CircuitDomainRecordInput, CircuitRecordDTO],
):
    required_fields = ("source_url", "infobox", "lap_record_rows", "sections")

    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[CircuitRecordDTO] | None = None,
    ) -> None:
        self._assembler = assembler or CircuitRecordAssembler()

    def _validate_input(self, input_dto: CircuitDomainRecordInput) -> None:
        self.validate_required(
            {
                "source_url": input_dto.source_url,
                "infobox": input_dto.infobox,
                "lap_record_rows": input_dto.lap_record_rows,
                "sections": input_dto.sections,
            },
            self.required_fields,
        )

    def build_payload(self, input_dto: CircuitDomainRecordInput) -> CircuitRecordDTO:
        return CircuitRecordDTO(
            url=input_dto.source_url,
            infobox=dict(input_dto.infobox),
            lap_record_rows=list(input_dto.lap_record_rows),
            sections=list(input_dto.sections),
        )

    def assemble(self, payload: CircuitRecordDTO) -> dict[str, Any]:
        return self._assembler.assemble(payload)

    def _compat_input_from_source(
        self,
        source: dict[str, Any],
    ) -> CircuitDomainRecordInput:
        return CircuitDomainRecordInput(
            source_url=str(source["source_url"]),
            infobox=dict(source["infobox"]),
            lap_record_rows=list(source["lap_record_rows"]),
            sections=list(source["sections"]),
        )
