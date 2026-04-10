from dataclasses import dataclass

from models.section_id import SectionId
from scrapers.sections.interface import SectionParser


@dataclass(frozen=True)
class SectionAdapterEntry:
    section_id: SectionId | str
    aliases: tuple[str, ...]
    parser: SectionParser
