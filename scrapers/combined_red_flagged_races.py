import warnings

from scrapers.legacy_impl.combined_red_flagged_races_impl import BaseRedFlaggedRacesTableParser
from scrapers.legacy_impl.combined_red_flagged_races_impl import NonChampionshipsRacesSubSectionParser
from scrapers.legacy_impl.combined_red_flagged_races_impl import NonChampionshipsRacesTableParser
from scrapers.legacy_impl.combined_red_flagged_races_impl import RESTART_STATUS_MAP
from scrapers.legacy_impl.combined_red_flagged_races_impl import RedFlaggedRacesScraper
from scrapers.legacy_impl.combined_red_flagged_races_impl import RedFlaggedRacesSectionParser
from scrapers.legacy_impl.combined_red_flagged_races_impl import WIKIPEDIA_BASE_URL
from scrapers.legacy_impl.combined_red_flagged_races_impl import WorldChampionshipsRacesTableParser
from scrapers.legacy_impl.combined_red_flagged_races_impl import build_full_url
from scrapers.legacy_impl.combined_red_flagged_races_impl import extract_rich_cell
from scrapers.legacy_impl.combined_red_flagged_races_impl import map_drivers_cell
from scrapers.legacy_impl.combined_red_flagged_races_impl import map_winner_cell
from scrapers.legacy_impl.combined_red_flagged_races_impl import try_int

warnings.warn(
    "combined_red_flagged_races is deprecated; use canonical scraper entrypoints.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "WIKIPEDIA_BASE_URL",
    "RESTART_STATUS_MAP",
    "build_full_url",
    "try_int",
    "extract_rich_cell",
    "map_winner_cell",
    "map_drivers_cell",
    "BaseRedFlaggedRacesTableParser",
    "WorldChampionshipsRacesTableParser",
    "NonChampionshipsRacesTableParser",
    "NonChampionshipsRacesSubSectionParser",
    "RedFlaggedRacesSectionParser",
    "RedFlaggedRacesScraper",
]
