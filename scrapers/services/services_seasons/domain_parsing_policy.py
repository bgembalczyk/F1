from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from scrapers.seasons.parsers_seasons import constants


class TestingVenuesLayout(str, Enum):
    __test__ = False
    STANDARD = "standard"
    SWAPPED_CIRCUIT_EVENT = "swapped_circuit_event"


@dataclass(frozen=True, slots=True)
class DomainParsingPolicy:
    """Reguły domenowe wykorzystywane przez parsery sezonu."""

    def resolve_engine_config(self, season_year: int | None) -> dict[str, Any] | None:
        if season_year == constants.ENGINE_V8_YEAR:
            return {"displacement_l": 2.4, "layout": "V", "cylinders": 8}
        if (
            season_year is not None
            and constants.ENGINE_V10_START_YEAR
            <= season_year
            <= constants.ENGINE_V10_END_YEAR
        ):
            return {"displacement_l": 3.0, "layout": "V", "cylinders": 10}
        return None

    def should_normalize_entry_numbers(self, season_year: int | None) -> bool:
        return (
            season_year is not None
            and season_year < constants.PRE_2007_NORMALIZATION_CUTOFF
        )

    def resolve_testing_venues_layout(
        self,
        season_year: int | None,
    ) -> TestingVenuesLayout | None:
        if season_year not in constants.TESTING_VENUES_YEARS:
            return None
        if season_year == constants.TESTING_VENUES_SWAPPED_COLUMNS_YEAR:
            return TestingVenuesLayout.SWAPPED_CIRCUIT_EVENT
        return TestingVenuesLayout.STANDARD
