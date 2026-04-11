from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from models.entity_name import EntityName
from models.section_id import SectionId
from scrapers.parsers.parse_result import ParseResult
from scrapers.types import JsonValue
from scrapers.types import PipelineRecord

SectionRecord: TypeAlias = PipelineRecord
SectionMetadata: TypeAlias = dict[str, JsonValue]
SectionUnifiedParseResult: TypeAlias = ParseResult[list[SectionRecord]]


@dataclass(frozen=True)
class SectionParseResult:
    """Unified output for domain section parsers."""

    section_id: SectionId
    section_label: EntityName
    records: list[SectionRecord]
    metadata: SectionMetadata

    def __post_init__(self) -> None:
        object.__setattr__(self, "section_id", SectionId.from_raw(self.section_id))
        object.__setattr__(
            self,
            "section_label",
            EntityName.from_raw(self.section_label),
        )


__all__ = [
    "SectionParseResult",
    "SectionRecord",
    "SectionMetadata",
    "SectionUnifiedParseResult",
]
