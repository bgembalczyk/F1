from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssemblerProtocol

from scrapers.drivers.drivers_postprocess.assembler import DriverRecordAssembler
from scrapers.drivers.drivers_postprocess.assembler import DriverRecordDTO
from scrapers.services.domain_record._shared import DomainRecordResult


@dataclass(frozen=True, slots=True)
class DriverDomainRecordInput:
    url: str
    infobox: dict[str, Any]
    career_results: list[dict[str, Any]]


class DomainRecordService:
    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[DriverRecordDTO] | None = None,
    ) -> None:
        self._assembler = assembler or DriverRecordAssembler()

    def execute(self, payload: DriverDomainRecordInput) -> DomainRecordResult:
        return DomainRecordResult(
            record=self._assembler.assemble(
                DriverRecordDTO(
                    url=payload.url,
                    infobox=payload.infobox,
                    career_results=payload.career_results,
                ),
            ),
        )
