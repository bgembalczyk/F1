from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from scrapers.records.assemblers.constructor import ConstructorRecordAssembler
from scrapers.records.dto.constructor import ConstructorRecordDTO
from scrapers.services.domain_record.base_pipeline_service import BaseDomainPipelineService



@dataclass(frozen=True, slots=True)
class ConstructorDomainRecordInput:
    url: str
    infoboxes: list[dict[str, Any]]
    tables: list[dict[str, Any]]
    sections: list[dict[str, Any]]


class ConstructorPipelineService(
    BaseDomainPipelineService[ConstructorDomainRecordInput, ConstructorRecordDTO],
):
    required_fields = ("url", "infoboxes", "tables", "sections")

    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[ConstructorRecordDTO] | None = None,
    ) -> None:
        self._assembler = assembler or ConstructorRecordAssembler()

    def _validate_input(self, input_dto: ConstructorDomainRecordInput) -> None:
        self.validate_required(
            {
                "url": input_dto.url,
                "infoboxes": input_dto.infoboxes,
                "tables": input_dto.tables,
                "sections": input_dto.sections,
            },
            self.required_fields,
        )

    def build_payload(
        self,
        input_dto: ConstructorDomainRecordInput,
    ) -> ConstructorRecordDTO:
        return ConstructorRecordDTO(
            url=input_dto.url,
            infoboxes=list(input_dto.infoboxes),
            tables=list(input_dto.tables),
            sections=list(input_dto.sections),
        )

    def assemble(self, payload: ConstructorRecordDTO) -> dict[str, Any]:
        return self._assembler.assemble(payload)

    def _compat_input_from_source(
        self,
        source: dict[str, Any],
    ) -> ConstructorDomainRecordInput:
        return ConstructorDomainRecordInput(
            url=str(source["url"]),
            infoboxes=list(source["infoboxes"]),
            tables=list(source["tables"]),
            sections=list(source["sections"]),
        )
