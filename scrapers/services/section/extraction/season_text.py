from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from scrapers.adapters.section.entry import SectionAdapterEntry
from scrapers.parsers.section.changes.season.mid_season import (
    SeasonMidSeasonChangesSectionParser,
)
from scrapers.parsers.section.changes.season.regulation import (
    SeasonRegulationChangesSectionParser,
)
from scrapers.parsers.section.wiki.helpers import profile_entry_aliases
from scrapers.services.section.extraction.base import BaseSectionExtractionService

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SeasonTextSectionExtractionService(BaseSectionExtractionService):
    domain = "seasons"
    aggregate_records_by_section_id = True
    _REGULATION_CHANGES_KEY = "regulation_changes"
    _MID_SEASON_CHANGES_KEY = "mid-season_changes"

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
        reg_changes = extracted.get(self._REGULATION_CHANGES_KEY, [])
        mid_changes = extracted.get(self._MID_SEASON_CHANGES_KEY, [])
        return {
            self._REGULATION_CHANGES_KEY: reg_changes,
            self._MID_SEASON_CHANGES_KEY: mid_changes,
            "Regulation_changes": reg_changes,
            "Mid-season_changes": mid_changes,
        }


__all__ = ["SeasonTextSectionExtractionService"]
