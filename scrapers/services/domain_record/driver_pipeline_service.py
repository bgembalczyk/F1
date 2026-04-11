from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.records.assemblers.driver import DriverRecordAssembler
from scrapers.records.dto.driver import DriverRecordDTO
from scrapers.services.domain_record.base_pipeline_service import (
    BaseDomainPipelineService,
)


@dataclass(frozen=True, slots=True)
class DriverDomainRecordInput:
    url: str
    infobox: dict[str, Any]
    career_results: list[dict[str, Any]]


class DriverPipelineService(
    BaseDomainPipelineService[DriverDomainRecordInput, DriverRecordDTO],
):
    required_fields = ("url", "infobox", "career_results")

    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[DriverRecordDTO] | None = None,
    ) -> None:
        self._assembler = assembler or DriverRecordAssembler()

    def _validate_input(self, input_dto: DriverDomainRecordInput) -> None:
        self.validate_required(
            {
                "url": input_dto.url,
                "infobox": input_dto.infobox,
                "career_results": input_dto.career_results,
            },
            self.required_fields,
        )

    def build_payload(self, input_dto: DriverDomainRecordInput) -> DriverRecordDTO:
        return DriverRecordDTO(
            url=input_dto.url,
            infobox=dict(input_dto.infobox),
            career_results=list(input_dto.career_results),
        )

    def assemble(self, payload: DriverRecordDTO) -> dict[str, Any]:
        return self._assembler.assemble(payload)

    def _compat_input_from_source(
        self,
        source: dict[str, Any],
    ) -> DriverDomainRecordInput:
        return DriverDomainRecordInput(
            url=str(source["url"]),
            infobox=dict(source["infobox"]),
            career_results=list(source["career_results"]),
        )
