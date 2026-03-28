from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssembler

from scrapers.drivers.postprocess.assembler import DriverRecordAssembler
from scrapers.drivers.postprocess.assembler import DriverRecordDTO


class DomainRecordService:
    def __init__(
        self,
        *,
        assembler: RecordAssembler[DriverRecordDTO] | None = None,
    ) -> None:
        self._assembler = assembler or DriverRecordAssembler()

    def assemble_record(
        self,
        *,
        url: str,
        infobox: dict[str, Any],
        career_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self._assembler.assemble(
            payload=DriverRecordDTO(
                url=url,
                infobox=infobox,
                career_results=career_results,
            ),
        )
