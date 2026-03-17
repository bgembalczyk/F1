from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.sections.critical_sections import resolve_section_candidates
from scrapers.base.sections.interface import SectionParser
from scrapers.base.sections.interface import SectionParseResult
from scrapers.wiki.parsers.section_detection import find_section_heading


@dataclass(frozen=True)
class SectionAdapterEntry:
    section_id: str
    aliases: tuple[str, ...]
    parser: SectionParser


class SectionAdapter(WikipediaSectionByIdMixin):
    @staticmethod
    def _extract_section_from_heading(
        soup: BeautifulSoup,
        heading_match,
    ) -> BeautifulSoup | None:
        header = heading_match.heading
        header_level = WikipediaSectionByIdMixin._get_header_level(header)
        heading_block = WikipediaSectionByIdMixin._get_heading_block(header)
        collected = WikipediaSectionByIdMixin._collect_section_siblings(
            heading_block,
            header_level,
        )
        html = "".join(str(node) for node in collected)
        if not html.strip():
            return None
        return BeautifulSoup(html, "html.parser")

    def parse_sections(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[SectionParseResult]:
        parsed: list[SectionParseResult] = []
        for entry in entries:
            entry_aliases = entry.aliases
            section_candidates = resolve_section_candidates(
                domain=domain,
                section_id=entry.section_id,
                alternative_section_ids=entry_aliases,
            )
            heading_match = None
            for candidate in section_candidates:
                heading_match = find_section_heading(
                    soup,
                    candidate,
                    aliases={
                        entry.section_id.lower().replace("_", " "): set(entry_aliases),
                    },
                    domain=domain,
                )
                if heading_match is not None:
                    break
            if heading_match is None:
                continue

            section_fragment = self._extract_section_from_heading(soup, heading_match)
            if section_fragment is None:
                continue
            parsed.append(entry.parser.parse(section_fragment))
        return parsed

    def parse_section_dicts(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[dict[str, Any]]:
        return [
            asdict(result)
            for result in self.parse_sections(soup=soup, domain=domain, entries=entries)
        ]
