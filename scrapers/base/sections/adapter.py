from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
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


class SectionAdapter(WikipediaSectionByIdMixin):
    @staticmethod
    def _get_header_level(header: Tag) -> int | None:
        try:
            return int(header.name[1])
        except (TypeError, ValueError, IndexError):
            return None

    @staticmethod
    def _get_heading_block(header: Tag) -> Tag:
        parent = header.parent
        if isinstance(parent, Tag):
            classes = parent.get("class") or []
            if (
                "mw-heading" in classes
                and parent.find(header.name, recursive=False) is header
            ):
                return parent
        return header

    @staticmethod
    def _extract_same_level_header(sibling: Tag) -> Tag | None:
        if sibling.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            return sibling
        if "mw-heading" in (sibling.get("class") or []):
            return sibling.find(["h1", "h2", "h3", "h4", "h5", "h6"], recursive=False)
        return None

    @staticmethod
    def _collect_section_siblings(
        heading_block: Tag,
        header_level: int | None,
    ) -> list[Any]:
        collected: list[Any] = [heading_block]
        for sib in heading_block.next_siblings:
            if isinstance(sib, Tag):
                same_level_header_tag = SectionAdapter._extract_same_level_header(sib)
                if same_level_header_tag is not None and header_level is not None:
                    sib_level = SectionAdapter._get_header_level(same_level_header_tag)
                    if sib_level == header_level:
                        break
            collected.append(sib)
        return collected

    @staticmethod
    def _extract_section_from_heading(
        heading_match,
    ) -> BeautifulSoup | None:
        header = heading_match.heading
        header_level = SectionAdapter._get_header_level(header)
        heading_block = SectionAdapter._get_heading_block(header)
        collected = SectionAdapter._collect_section_siblings(
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
