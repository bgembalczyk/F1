from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.base.sections.interface import SectionParser
from scrapers.wiki.parsers.section_profiles import profile_entry_aliases


@dataclass(frozen=True)
class SectionEntrySpec:
    section_id: str
    aliases: tuple[str, ...]
    parser_factory: Callable[[], SectionParser]


def section_entries_from_specs(
    *,
    domain: str,
    specs: list[SectionEntrySpec],
) -> list[SectionAdapterEntry]:
    return [
        SectionAdapterEntry(
            section_id=spec.section_id,
            aliases=profile_entry_aliases(domain, spec.section_id, *spec.aliases),
            parser=spec.parser_factory(),
        )
        for spec in specs
    ]

