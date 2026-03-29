from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.circuits.sections.events import CircuitEventsSectionParser
from scrapers.circuits.sections.lap_records import CircuitLapRecordsSectionParser
from scrapers.circuits.sections.layout_history import CircuitLayoutHistorySectionParser
from scrapers.wiki.parsers.sections.helpers import profile_entry_aliases

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions


def circuit_section_entries(
    *,
    options: ScraperOptions,
    url: str,
) -> list[SectionAdapterEntry]:
    return [
        SectionAdapterEntry(
            section_id="layout_history",
            aliases=profile_entry_aliases(
                "circuits",
                "layout_history",
                "Layout_history",
                "History",
            ),
            parser=CircuitLayoutHistorySectionParser(),
        ),
        SectionAdapterEntry(
            section_id="lap_records",
            aliases=profile_entry_aliases(
                "circuits",
                "lap_records",
                "Lap_records",
                "Formula_One_lap_records",
            ),
            parser=CircuitLapRecordsSectionParser(
                options=options,
                url=url,
            ),
        ),
        SectionAdapterEntry(
            section_id="events",
            aliases=profile_entry_aliases("circuits", "events", "Events", "Races"),
            parser=CircuitEventsSectionParser(),
        ),
    ]
