from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup

from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.interface import SectionParser


@dataclass(frozen=True)
class SectionAdapterEntry:
    section_id: str
    aliases: tuple[str, ...]
    parser: SectionParser


class SectionAdapter(WikipediaSectionByIdMixin):
    def parse_sections(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[SectionParseResult]:
        parsed: list[SectionParseResult] = []
        for entry in entries:
            section_fragment = None
            for section_id in [entry.section_id, *entry.aliases]:
                section_fragment = self.extract_section_by_id(
                    soup,
                    section_id,
                    domain=domain,
                )
                if section_fragment is not None:
                    break
            if section_fragment is None:
                continue
            parsed.append(entry.parser.parse(section_fragment))
        return parsed
