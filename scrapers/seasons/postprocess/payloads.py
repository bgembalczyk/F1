from __future__ import annotations

from dataclasses import dataclass

from scrapers.base.payloads import SectionsPayload
from scrapers.seasons.postprocess.assembler import SeasonRecordSections


@dataclass(frozen=True)
class SeasonSectionsPayload(SectionsPayload):
    sections: SeasonRecordSections

    def __init__(self, sections: SeasonRecordSections) -> None:
        super().__init__(data=[])
        object.__setattr__(self, "sections", sections)
