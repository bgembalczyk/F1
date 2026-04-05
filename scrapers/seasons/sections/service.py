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
    _REGULATION_CHANGES_KEY = "regulation_changes"
    _MID_SEASON_CHANGES_KEY = "mid-season_changes"
    _REGULATION_CHANGES_LEGACY_KEY = "Regulation_changes"
    _MID_SEASON_CHANGES_LEGACY_KEY = "Mid-season_changes"

    def build_entries(self) -> list[SectionAdapterEntry]:
        return [
            SectionAdapterEntry(
                section_id=self._REGULATION_CHANGES_KEY,
                aliases=profile_entry_aliases(
                    self.domain,
                    "Regulation_changes",
                    "Rule_changes",
                ),
                parser=SeasonRegulationChangesSectionParser(),
            ),
            SectionAdapterEntry(
                section_id=self._MID_SEASON_CHANGES_KEY,
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
        extracted = cast("dict[str, list[dict[str, Any]]]", super().extract(soup))
        regulation_changes = extracted.get(self._REGULATION_CHANGES_KEY, [])
        mid_season_changes = extracted.get(self._MID_SEASON_CHANGES_KEY, [])
        return {
            self._REGULATION_CHANGES_KEY: regulation_changes,
            self._MID_SEASON_CHANGES_KEY: mid_season_changes,
            self._REGULATION_CHANGES_LEGACY_KEY: regulation_changes,
            self._MID_SEASON_CHANGES_LEGACY_KEY: mid_season_changes,
        }
