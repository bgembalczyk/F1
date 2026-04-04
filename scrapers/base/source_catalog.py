"""Canonical source catalog for Wikipedia-based scrapers.

Centralizes article paths and section ids used by domain ``CONFIG`` definitions.
"""

from __future__ import annotations

from dataclasses import dataclass

WIKIPEDIA_BASE_URL = "https://en.wikipedia.org/wiki"


@dataclass(frozen=True)
class SourceRef:
    """Catalog entry for a Wikipedia article and its default section id."""

    article: str
    section_id: str | None = None

    @property
    def base_url(self) -> str:
        """Stable convenience API kept for scraper configs expecting article-only URL."""
        return wiki_article_url(self.article)

    def url(self, *, section_id: str | None = None) -> str:
        """Stable boundary API for building source URL with default or overridden section."""
        return wiki_article_url(self.article, section_id=section_id or self.section_id)


def wiki_article_url(article: str, *, section_id: str | None = None) -> str:
    """Build canonical ``/wiki`` URL with optional section id fragment."""

    base_url = f"{WIKIPEDIA_BASE_URL}/{article}"
    return append_section_id(base_url, section_id)


def append_section_id(base_url: str, section_id: str | None) -> str:
    """Append section id as URL fragment.

    Accepts already-normalized section ids used by scraper configs.
    """

    if not section_id:
        return base_url
    return f"{base_url}#{section_id}"


DRIVERS_LIST = SourceRef("List_of_Formula_One_drivers", section_id="Drivers")
DRIVERS_FATALITIES = SourceRef(
    "List_of_Formula_One_fatalities",
    section_id="Detail_by_driver",
)
FEMALE_DRIVERS_LIST = SourceRef(
    "List_of_female_Formula_One_drivers",
    section_id="Formula_One_drivers",
)

CONSTRUCTORS_LIST = SourceRef(
    "List_of_Formula_One_constructors",
)

CIRCUITS_LIST = SourceRef("List_of_Formula_One_circuits", section_id="Circuits")
GRANDS_PRIX_LIST = SourceRef(
    "List_of_Formula_One_Grands_Prix",
    section_id="By_race_title",
)
SEASONS_LIST = SourceRef("List_of_Formula_One_seasons", section_id="Seasons")

POINTS_SCORING_SYSTEMS = SourceRef(
    "List_of_Formula_One_World_Championship_points_scoring_systems",
)

ENGINES_LIST = SourceRef(
    "List_of_Formula_One_engine_manufacturers",
    section_id="Engine_manufacturers",
)
ENGINE_REGULATIONS = SourceRef(
    "Formula_One_regulations",
    section_id="Engine",
)
ENGINE_PROGRESS = SourceRef(
    "Formula_One_engines",
    section_id="Engine_regulation_progression_by_era",
)

RED_FLAGGED_RACES = SourceRef(
    "List_of_red-flagged_Formula_One_races",
    section_id="Red-flagged_races",
)

TYRES = SourceRef("Formula_One_tyres", section_id="Tyre_manufacturers_by_season")
