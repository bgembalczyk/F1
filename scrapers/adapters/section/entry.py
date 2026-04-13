from dataclasses import dataclass

from models.section_id import SectionId
from scrapers.parsers.section.base import SectionParserBase


@dataclass(frozen=True)
class SectionAdapterEntry:
    section_id: SectionId | str
    aliases: tuple[str, ...]
    parser: SectionParserBase
