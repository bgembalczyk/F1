from __future__ import annotations

from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.circuits.sections.events import CircuitEventsSectionParser
from scrapers.circuits.sections.lap_records import CircuitLapRecordsSectionParser
from scrapers.circuits.sections.layout_history import CircuitLayoutHistorySectionParser


def circuit_section_entries(*, options: ScraperOptions, url: str) -> list[SectionAdapterEntry]:
    return [
        SectionAdapterEntry(
            section_id="layout_history",
            aliases=("Layout_history", "History"),
            parser=CircuitLayoutHistorySectionParser(),
        ),
        SectionAdapterEntry(
            section_id="lap_records",
            aliases=("Lap_records", "Formula_One_lap_records"),
            parser=CircuitLapRecordsSectionParser(
                options=options,
                url=url,
            ),
        ),
        SectionAdapterEntry(
            section_id="events",
            aliases=("Events", "Races"),
            parser=CircuitEventsSectionParser(),
        ),
    ]
