from dataclasses import asdict
from dataclasses import dataclass
from typing import Any

from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.constructors.current_constructors_list import (
    CurrentConstructorsListScraper,
)
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.drivers.fatalities_list_scraper import F1FatalitiesListScraper
from scrapers.drivers.female_drivers_list import FemaleDriversListScraper
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.engine_regulation import EngineRegulationScraper
from scrapers.engines.engine_restrictions import EngineRestrictionsScraper
from scrapers.engines.indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.grands_prix.red_flagged_races_scraper.non_championship import (
    RedFlaggedNonChampionshipRacesScraper,
)
from scrapers.grands_prix.red_flagged_races_scraper.world_championship import (
    RedFlaggedWorldChampionshipRacesScraper,
)
from scrapers.points.points_scoring_systems_history import (
    PointsScoringSystemsHistoryScraper,
)
from scrapers.points.shortened_race_points import ShortenedRacePointsScraper
from scrapers.points.sprint_qualifying_points import SprintQualifyingPointsScraper
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.sponsorship_liveries.scraper import F1SponsorshipLiveriesScraper
from scrapers.tyres.list_scraper import TyreManufacturersBySeasonScraper


@dataclass(frozen=True)
class SeedRegistryEntry:
    seed_name: str
    wikipedia_url: str
    output_category: str
    list_scraper_cls: type[Any]
    default_output_path: str
    legacy_output_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ListJobRegistryEntry:
    seed_name: str
    wikipedia_url: str
    output_category: str
    list_scraper_cls: type[Any]
    json_output_path: str
    legacy_json_output_path: str
    csv_output_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


WIKI_SEED_REGISTRY: tuple[SeedRegistryEntry, ...] = (
    SeedRegistryEntry(
        seed_name="drivers",
        wikipedia_url=F1DriversListScraper.CONFIG.url,
        output_category="drivers",
        list_scraper_cls=F1DriversListScraper,
        default_output_path="raw/drivers/seeds/complete_drivers",
        legacy_output_path="drivers/complete_drivers",
    ),
    SeedRegistryEntry(
        seed_name="constructors",
        wikipedia_url=CurrentConstructorsListScraper.CONFIG.url,
        output_category="constructors",
        list_scraper_cls=CurrentConstructorsListScraper,
        default_output_path="raw/constructors/seeds/complete_constructors",
        legacy_output_path="constructors/complete_constructors",
    ),
    SeedRegistryEntry(
        seed_name="grands_prix",
        wikipedia_url=GrandsPrixListScraper.CONFIG.url,
        output_category="grands_prix",
        list_scraper_cls=GrandsPrixListScraper,
        default_output_path="raw/grands_prix/seeds/f1_grands_prix_extended.json",
        legacy_output_path="grands_prix/f1_grands_prix_extended.json",
    ),
    SeedRegistryEntry(
        seed_name="circuits",
        wikipedia_url=CircuitsListScraper.CONFIG.url,
        output_category="circuits",
        list_scraper_cls=CircuitsListScraper,
        default_output_path="raw/circuits/seeds/complete_circuits",
        legacy_output_path="circuits/complete_circuits",
    ),
    SeedRegistryEntry(
        seed_name="seasons",
        wikipedia_url=SeasonsListScraper.CONFIG.url,
        output_category="seasons",
        list_scraper_cls=SeasonsListScraper,
        default_output_path="raw/seasons/seeds/complete_seasons",
        legacy_output_path="seasons/complete_seasons",
    ),
)


WIKI_LIST_JOB_REGISTRY: tuple[ListJobRegistryEntry, ...] = (
    ListJobRegistryEntry(
        seed_name="circuits",
        wikipedia_url=CircuitsListScraper.CONFIG.url,
        output_category="circuits",
        list_scraper_cls=CircuitsListScraper,
        json_output_path="raw/circuits/list/f1_circuits.json",
        legacy_json_output_path="circuits/f1_circuits.json",
    ),
    ListJobRegistryEntry(
        seed_name="constructors_current",
        wikipedia_url=CurrentConstructorsListScraper.CONFIG.url,
        output_category="constructors",
        list_scraper_cls=CurrentConstructorsListScraper,
        json_output_path="raw/constructors/list/f1_constructors_{year}.json",
        legacy_json_output_path="constructors/f1_constructors_{year}.json",
    ),
    ListJobRegistryEntry(
        seed_name="constructors_former",
        wikipedia_url=FormerConstructorsListScraper.CONFIG.url,
        output_category="constructors",
        list_scraper_cls=FormerConstructorsListScraper,
        json_output_path="raw/constructors/list/f1_former_constructors.json",
        legacy_json_output_path="constructors/f1_former_constructors.json",
    ),
    ListJobRegistryEntry(
        seed_name="constructors_indianapolis_only",
        wikipedia_url=IndianapolisOnlyConstructorsListScraper.url,
        output_category="constructors",
        list_scraper_cls=IndianapolisOnlyConstructorsListScraper,
        json_output_path="raw/constructors/list/f1_indianapolis_only_constructors.json",
        legacy_json_output_path="constructors/f1_indianapolis_only_constructors.json",
    ),
    ListJobRegistryEntry(
        seed_name="constructors_privateer",
        wikipedia_url=PrivateerTeamsListScraper.url,
        output_category="constructors",
        list_scraper_cls=PrivateerTeamsListScraper,
        json_output_path="raw/constructors/list/f1_privateer_teams.json",
        legacy_json_output_path="constructors/f1_privateer_teams.json",
    ),
    ListJobRegistryEntry(
        seed_name="drivers",
        wikipedia_url=F1DriversListScraper.CONFIG.url,
        output_category="drivers",
        list_scraper_cls=F1DriversListScraper,
        json_output_path="raw/drivers/list/f1_drivers.json",
        legacy_json_output_path="drivers/f1_drivers.json",
    ),
    ListJobRegistryEntry(
        seed_name="drivers_female",
        wikipedia_url=FemaleDriversListScraper.CONFIG.url,
        output_category="drivers",
        list_scraper_cls=FemaleDriversListScraper,
        json_output_path="raw/drivers/list/female_drivers.json",
        legacy_json_output_path="drivers/female_drivers.json",
    ),
    ListJobRegistryEntry(
        seed_name="drivers_fatalities",
        wikipedia_url=F1FatalitiesListScraper.CONFIG.url,
        output_category="drivers",
        list_scraper_cls=F1FatalitiesListScraper,
        json_output_path="raw/drivers/list/f1_driver_fatalities.json",
        legacy_json_output_path="drivers/f1_driver_fatalities.json",
    ),
    ListJobRegistryEntry(
        seed_name="engines_indianapolis_only",
        wikipedia_url=IndianapolisOnlyEngineManufacturersListScraper.url,
        output_category="engines",
        list_scraper_cls=IndianapolisOnlyEngineManufacturersListScraper,
        json_output_path="raw/engines/list/f1_indianapolis_only_engine_manufacturers.json",
        legacy_json_output_path="engines/f1_indianapolis_only_engine_manufacturers.json",
    ),
    ListJobRegistryEntry(
        seed_name="engines_restrictions",
        wikipedia_url=EngineRestrictionsScraper.CONFIG.url,
        output_category="engines",
        list_scraper_cls=EngineRestrictionsScraper,
        json_output_path="raw/engines/list/f1_engine_restrictions.json",
        legacy_json_output_path="engines/f1_engine_restrictions.json",
    ),
    ListJobRegistryEntry(
        seed_name="engines_regulations",
        wikipedia_url=EngineRegulationScraper.CONFIG.url,
        output_category="engines",
        list_scraper_cls=EngineRegulationScraper,
        json_output_path="raw/engines/list/f1_engine_regulations.json",
        legacy_json_output_path="engines/f1_engine_regulations.json",
    ),
    ListJobRegistryEntry(
        seed_name="engines_manufacturers",
        wikipedia_url=EngineManufacturersListScraper.CONFIG.url,
        output_category="engines",
        list_scraper_cls=EngineManufacturersListScraper,
        json_output_path="raw/engines/list/f1_engine_manufacturers.json",
        legacy_json_output_path="engines/f1_engine_manufacturers.json",
    ),
    ListJobRegistryEntry(
        seed_name="grands_prix_red_flagged_world_championship",
        wikipedia_url=RedFlaggedWorldChampionshipRacesScraper.CONFIG.url,
        output_category="grands_prix",
        list_scraper_cls=RedFlaggedWorldChampionshipRacesScraper,
        json_output_path="raw/grands_prix/list/f1_red_flagged_world_championship_races.json",
        legacy_json_output_path="grands_prix/f1_red_flagged_world_championship_races.json",
    ),
    ListJobRegistryEntry(
        seed_name="grands_prix_red_flagged_non_championship",
        wikipedia_url=RedFlaggedNonChampionshipRacesScraper.CONFIG.url,
        output_category="grands_prix",
        list_scraper_cls=RedFlaggedNonChampionshipRacesScraper,
        json_output_path="raw/grands_prix/list/f1_red_flagged_non_championship_races.json",
        legacy_json_output_path="grands_prix/f1_red_flagged_non_championship_races.json",
    ),
    ListJobRegistryEntry(
        seed_name="points_sprint",
        wikipedia_url=SprintQualifyingPointsScraper.CONFIG.url,
        output_category="points",
        list_scraper_cls=SprintQualifyingPointsScraper,
        json_output_path="raw/points/list/points_scoring_systems_sprint.json",
        legacy_json_output_path="points/points_scoring_systems_sprint.json",
    ),
    ListJobRegistryEntry(
        seed_name="points_shortened",
        wikipedia_url=ShortenedRacePointsScraper.CONFIG.url,
        output_category="points",
        list_scraper_cls=ShortenedRacePointsScraper,
        json_output_path="raw/points/list/points_scoring_systems_shortened.json",
        legacy_json_output_path="points/points_scoring_systems_shortened.json",
    ),
    ListJobRegistryEntry(
        seed_name="points_history",
        wikipedia_url=PointsScoringSystemsHistoryScraper.CONFIG.url,
        output_category="points",
        list_scraper_cls=PointsScoringSystemsHistoryScraper,
        json_output_path="raw/points/list/points_scoring_systems_history.json",
        legacy_json_output_path="points/points_scoring_systems_history.json",
    ),
    ListJobRegistryEntry(
        seed_name="tyres",
        wikipedia_url=TyreManufacturersBySeasonScraper.CONFIG.url,
        output_category="tyres",
        list_scraper_cls=TyreManufacturersBySeasonScraper,
        json_output_path="raw/tyres/list/f1_tyre_manufacturers_by_season.json",
        legacy_json_output_path="tyres/f1_tyre_manufacturers_by_season.json",
    ),
    ListJobRegistryEntry(
        seed_name="sponsorship_liveries",
        wikipedia_url=F1SponsorshipLiveriesScraper.url,
        output_category="sponsorship_liveries",
        list_scraper_cls=F1SponsorshipLiveriesScraper,
        json_output_path="raw/sponsorship_liveries/list/f1_sponsorship_liveries.json",
        legacy_json_output_path="sponsorship_liveries/f1_sponsorship_liveries.json",
    ),
)


def validate_seed_registry(
    registry: tuple[SeedRegistryEntry, ...] = WIKI_SEED_REGISTRY,
) -> None:
    seen_seed_names: set[str] = set()

    for entry in registry:
        if entry.seed_name in seen_seed_names:
            msg = f"Duplicate seed_name found: {entry.seed_name}"
            raise ValueError(msg)
        seen_seed_names.add(entry.seed_name)

        if not entry.wikipedia_url.strip():
            msg = f"Seed '{entry.seed_name}' has empty wikipedia_url"
            raise ValueError(msg)

        expected_prefix = f"raw/{entry.output_category}/"
        if not entry.default_output_path.startswith(expected_prefix):
            msg = (
                f"Seed '{entry.seed_name}' has inconsistent output path "
                f"'{entry.default_output_path}' for category '{entry.output_category}'"
            )
            raise ValueError(msg)

        legacy_prefix = f"{entry.output_category}/"
        if not entry.legacy_output_path.startswith(legacy_prefix):
            msg = (
                f"Seed '{entry.seed_name}' has inconsistent legacy output path "
                f"'{entry.legacy_output_path}' for category '{entry.output_category}'"
            )
            raise ValueError(msg)


def validate_list_job_registry(
    registry: tuple[ListJobRegistryEntry, ...] = WIKI_LIST_JOB_REGISTRY,
) -> None:
    seen_seed_names: set[str] = set()

    for entry in registry:
        if entry.seed_name in seen_seed_names:
            msg = f"Duplicate list seed_name found: {entry.seed_name}"
            raise ValueError(msg)
        seen_seed_names.add(entry.seed_name)

        expected_prefix = f"raw/{entry.output_category}/"
        if not entry.json_output_path.startswith(expected_prefix):
            msg = (
                f"List seed '{entry.seed_name}' has inconsistent output path "
                f"'{entry.json_output_path}' for category '{entry.output_category}'"
            )
            raise ValueError(msg)

        if not entry.wikipedia_url.strip():
            msg = f"List seed '{entry.seed_name}' has empty wikipedia_url"
            raise ValueError(msg)

        legacy_prefix = f"{entry.output_category}/"
        if not entry.legacy_json_output_path.startswith(legacy_prefix):
            msg = (
                f"List seed '{entry.seed_name}' has inconsistent legacy output path "
                f"'{entry.legacy_json_output_path}' for category '{entry.output_category}'"
            )
            raise ValueError(msg)
