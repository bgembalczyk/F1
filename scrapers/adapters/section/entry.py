from dataclasses import dataclass

from models.section_id import SectionId
from scrapers.parsers.wiki.sections.nested_wiki_section_parser import NestedWikiSectionParser


@dataclass(frozen=True)
class SectionAdapterEntry:
    section_id: SectionId | str
    aliases: tuple[str, ...]
    parser: NestedWikiSectionParser
