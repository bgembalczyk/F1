from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.seasons.sections.mid_season_changes import (
    SeasonMidSeasonChangesSectionParser,
)
from scrapers.seasons.sections.regulation_changes import (
    SeasonRegulationChangesSectionParser,
)
from scrapers.wiki.parsers.section_profiles import profile_entry_aliases

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SeasonTextSectionExtractionService:
    def __init__(self, *, adapter: SectionAdapter) -> None:
        self._adapter = adapter

    def extract(self, soup: BeautifulSoup) -> dict[str, list[dict[str, Any]]]:
        text_sections = self._adapter.parse_sections(
            soup=soup,
            domain="seasons",
            entries=[
                SectionAdapterEntry(
                    section_id="Regulation_changes",
                    aliases=profile_entry_aliases(
                        "seasons",
                        "Regulation_changes",
                        "Rule_changes",
                    ),
                    parser=SeasonRegulationChangesSectionParser(),
                ),
                SectionAdapterEntry(
                    section_id="Mid-season_changes",
                    aliases=profile_entry_aliases(
                        "seasons",
                        "Mid-season_changes",
                        "Driver_changes",
                    ),
                    parser=SeasonMidSeasonChangesSectionParser(),
                ),
            ],
        )
        return {result.section_id: result.records for result in text_sections}
