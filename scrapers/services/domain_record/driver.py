from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssemblerProtocol

from scrapers.drivers.drivers_postprocess.assembler import DriverRecordAssembler
from scrapers.drivers.drivers_postprocess.assembler import DriverRecordDTO
from scrapers.services.domain_record.base import BaseDomainRecordService


@dataclass(frozen=True, slots=True)
class DriverDomainRecordInput:
    url: str
    infobox: dict[str, Any]
    career_results: list[dict[str, Any]]


class DriverDomainRecordService(BaseDomainRecordService[DriverDomainRecordInput]):
    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[DriverRecordDTO] | None = None,
    ) -> None:
        self._assembler = assembler or DriverRecordAssembler()

    def assemble_record(self, payload: DriverDomainRecordInput) -> dict[str, Any]:
        return self._assembler.assemble(
            DriverRecordDTO(
                url=payload.url,
                infobox=payload.infobox,
                career_results=payload.career_results,
            ),
        )


class DomainRecordService(DriverDomainRecordService):
    """Compatibility alias for legacy imports."""
