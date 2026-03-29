from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from models.value_objects.common_terms import SectionId
from scrapers.base.sections.section_id_resolver import SectionIdResolver
from scrapers.base.sections.serializer import serialize_section_result
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.wiki.parsers.sections.helpers import profile_entry_aliases

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.sections.interface import SectionParser
    from scrapers.base.sections.interface import SectionParseResult


@dataclass(frozen=True)
class SectionAdapterEntry:
    section_id: SectionId | str
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
        resolver = SectionIdResolver(domain=domain)
        for entry in entries:
            section_id = SectionId.from_raw(entry.section_id)
            entry_aliases = profile_entry_aliases(
                domain,
                section_id.to_export(),
                *entry.aliases,
            )
            resolution = resolver.resolve_heading(
                soup=soup,
                section_id=section_id,
                alternative_section_ids=entry_aliases,
                aliases={
                    section_id.to_export().replace("_", " "): set(entry_aliases),
                },
            )
            if resolution.heading_match is None:
                continue

            section_fragment = self._extract_section_from_heading(
                resolution.heading_match,
            )
            if section_fragment is None:
                continue
            parsed.append(entry.parser.parse(section_fragment))
        return parsed

    def assemble_section_dicts(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[dict[str, Any]]:
        return [
            serialize_section_result(result)
            for result in self.parse_sections(soup=soup, domain=domain, entries=entries)
        ]

    def parse_section_dicts(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[dict[str, Any]]:
        warnings.warn(
            "SectionAdapter.parse_section_dicts() is deprecated; use "
            "assemble_section_dicts() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.assemble_section_dicts(soup=soup, domain=domain, entries=entries)
