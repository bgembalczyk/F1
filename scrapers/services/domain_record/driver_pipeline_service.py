from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.drivers.drivers_postprocess.assembler import DriverRecordAssembler
from scrapers.drivers.drivers_postprocess.assembler import DriverRecordDTO
from scrapers.services.domain_record.base_pipeline_service import BaseFactoryScraper

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssemblerProtocol


class DriverPipelineService(BaseFactoryScraper[DriverRecordDTO]):
    required_fields = ("url", "infobox", "career_results")

    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[DriverRecordDTO] | None = None,
    ) -> None:
        self._assembler = assembler or DriverRecordAssembler()

    def _build_payload(self, source: dict[str, Any]) -> DriverRecordDTO:
        return DriverRecordDTO(
            url=str(source["url"]),
            infobox=dict(source["infobox"]),
            career_results=list(source["career_results"]),
        )

    def _assemble(self, payload: DriverRecordDTO) -> dict[str, Any]:
        return self._assembler.assemble(payload)

    def assemble_record(
        self,
        *,
        url: str,
        infobox: dict[str, Any],
        career_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self.run(
            {
                "url": url,
                "infobox": infobox,
                "career_results": career_results,
            },
        )
