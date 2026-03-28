from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.base.sections.resolve_candidates import resolve_section_candidates
from scrapers.wiki.parsers.section_detection import find_section_heading
from scrapers.wiki.parsers.section_profiles import profile_entry_aliases

if TYPE_CHECKING:
    from scrapers.base.sections.interface import SectionParser
    from scrapers.base.sections.interface import SectionParseResult


@dataclass(frozen=True)
class SectionAdapterEntry:
    section_id: str
    aliases: tuple[str, ...]
    parser: SectionParser


class SectionAdapter:
    @classmethod
    def _extract_section_from_heading(cls, heading_match) -> BeautifulSoup | None:
        return WikipediaSectionByIdSelectionStrategy.extract_section_by_heading(
            heading_match.heading,
        )

    def parse_sections(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[SectionParseResult]:
        parsed: list[SectionParseResult] = []
        for entry in entries:
            entry_aliases = profile_entry_aliases(
                domain,
                entry.section_id,
                *entry.aliases,
            )
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

            section_fragment = self._extract_section_from_heading(heading_match)
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
