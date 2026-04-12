from dataclasses import dataclass

from models.section_id import SectionId
from scrapers.parsers.contracts.sections import SectionStructureParserABC


@dataclass(frozen=True)
class SectionAdapterEntry:
    section_id: SectionId | str
    aliases: tuple[str, ...]
    parser: SectionStructureParserABC
