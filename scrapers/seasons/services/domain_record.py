from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssembler

from scrapers.seasons.postprocess.assembler import SeasonPayloadDTO
from scrapers.seasons.postprocess.assembler import SeasonRecordAssembler
from scrapers.seasons.postprocess.assembler import SeasonRecordSections


class DomainRecordService:
    def __init__(self, *, assembler: RecordAssembler[SeasonRecordSections] | None = None) -> None:
        self._assembler = assembler or SeasonRecordAssembler()

    def build_sections_payload(
        self,
        payload: SeasonPayloadDTO | Any,
    ) -> SeasonRecordSections:
        if not isinstance(payload, SeasonPayloadDTO):
            return SeasonRecordSections.empty()
        return payload.sections

    def assemble_record(self, sections: SeasonRecordSections) -> dict[str, Any]:
        return self._assembler.assemble(sections)
