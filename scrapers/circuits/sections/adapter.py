from __future__ import annotations

from scrapers.base.options import ScraperOptions
from scrapers.base.sections.entry_factory import SectionEntrySpec
from scrapers.base.sections.entry_factory import section_entries_from_specs
from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.circuits.sections.events import CircuitEventsSectionParser
from scrapers.circuits.sections.lap_records import CircuitLapRecordsSectionParser
from scrapers.circuits.sections.layout_history import CircuitLayoutHistorySectionParser


def circuit_section_entries(
    *,
    options: ScraperOptions,
    url: str,
) -> list[SectionAdapterEntry]:
    specs = [
        SectionEntrySpec(
            section_id="layout_history",
            aliases=("Layout_history", "History"),
            parser_factory=CircuitLayoutHistorySectionParser,
        ),
        SectionEntrySpec(
            section_id="lap_records",
            aliases=("Lap_records", "Formula_One_lap_records"),
            parser_factory=lambda: CircuitLapRecordsSectionParser(
                options=options,
                url=url,
            ),
        ),
        SectionEntrySpec(
            section_id="events",
            aliases=("Events", "Races"),
            parser_factory=CircuitEventsSectionParser,
        ),
    ]
    return section_entries_from_specs(domain="circuits", specs=specs)
