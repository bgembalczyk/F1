from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.base.sections.service import BaseSectionExtractionService
from scrapers.seasons.sections.mid_season_changes import (
    SeasonMidSeasonChangesSectionParser,
)
from scrapers.seasons.sections.regulation_changes import (
    SeasonRegulationChangesSectionParser,
)
from scrapers.wiki.parsers.sections.helpers import profile_entry_aliases

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SeasonTextSectionExtractionService(BaseSectionExtractionService):
    domain = "seasons"
    aggregate_records_by_section_id = True

    def build_entries(self) -> list[SectionAdapterEntry]:
        return [
            SectionAdapterEntry(
                section_id="Regulation_changes",
                aliases=profile_entry_aliases(
                    self.domain,
                    "Regulation_changes",
                    "Rule_changes",
                ),
                parser=SeasonRegulationChangesSectionParser(),
            ),
            SectionAdapterEntry(
                section_id="Mid-season_changes",
                aliases=profile_entry_aliases(
                    self.domain,
                    "Mid-season_changes",
                    "Driver_changes",
                ),
                parser=SeasonMidSeasonChangesSectionParser(),
            ),
        ]

    def extract(self, soup: BeautifulSoup) -> dict[str, list[dict[str, Any]]]:
        # Utrzymujemy kontrakt sezonowego pipeline'u: mapowanie section_id -> records.
        return cast(dict[str, list[dict[str, Any]]], super().extract(soup))
