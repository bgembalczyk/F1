from datetime import UTC
from datetime import datetime
from pathlib import Path

from infrastructure.gemini.client import GeminiClient
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig

# List scrapers
from scrapers.circuits.helpers.export import export_complete_circuits
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.constructors.current_constructors_list import (
    CurrentConstructorsListScraper,
)
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.helpers.export import export_complete_constructors
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.drivers.fatalities_list_scraper import F1FatalitiesListScraper
from scrapers.drivers.female_drivers_list import FemaleDriversListScraper
from scrapers.drivers.helpers.export import export_complete_drivers
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.engine_regulation import EngineRegulationScraper
from scrapers.engines.engine_restrictions import EngineRestrictionsScraper
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.engines.indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor
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
from scrapers.seasons.helpers import export_complete_seasons
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier
from scrapers.sponsorship_liveries.scraper import F1SponsorshipLiveriesScraper
from scrapers.tyres.list_scraper import TyreManufacturersBySeasonScraper

# Ścieżki wyjściowe względem katalogu repo (ten plik jest w root)
BASE_WIKI_DIR = Path("data/wiki").resolve()
BASE_DEBUG_DIR = Path("data/debug").resolve()
CURRENT_YEAR = datetime.now(tz=UTC).year


def run_list_scrapers() -> None:
    run_config = RunConfig(
        output_dir=BASE_WIKI_DIR,
        include_urls=True,
        debug_dir=BASE_DEBUG_DIR,
    )

    jobs: list[tuple[object, str, str | None]] = [
        (CircuitsListScraper, "circuits/f1_circuits.json", None),
        (
            CurrentConstructorsListScraper,
            f"constructors/f1_constructors_{CURRENT_YEAR}.json",
            None,
        ),
        (
            FormerConstructorsListScraper,
            "constructors/f1_former_constructors.json",
            None,
        ),
        (
            IndianapolisOnlyConstructorsListScraper,
            "constructors/f1_indianapolis_only_constructors.json",
            None,
        ),
        (
            PrivateerTeamsListScraper,
            "constructors/f1_privateer_teams.json",
            None,
        ),
        (F1DriversListScraper, "drivers/f1_drivers.json", None),
        (FemaleDriversListScraper, "drivers/female_drivers.json", None),
        (F1FatalitiesListScraper, "drivers/f1_driver_fatalities.json", None),
        (
            IndianapolisOnlyEngineManufacturersListScraper,
            "engines/f1_indianapolis_only_engine_manufacturers.json",
            None,
        ),
        (EngineRestrictionsScraper, "engines/f1_engine_restrictions.json", None),
        (EngineRegulationScraper, "engines/f1_engine_regulations.json", None),
        (
            EngineManufacturersListScraper,
            "engines/f1_engine_manufacturers.json",
            None,
        ),
        (
            RedFlaggedWorldChampionshipRacesScraper,
            "grands_prix/f1_red_flagged_world_championship_races.json",
            None,
        ),
        (
            RedFlaggedNonChampionshipRacesScraper,
            "grands_prix/f1_red_flagged_non_championship_races.json",
            None,
        ),
        (
            SprintQualifyingPointsScraper,
            "points/points_scoring_systems_sprint.json",
            None,
        ),
        (
            ShortenedRacePointsScraper,
            "points/points_scoring_systems_shortened.json",
            None,
        ),
        (
            PointsScoringSystemsHistoryScraper,
            "points/points_scoring_systems_history.json",
            None,
        ),
        (
            TyreManufacturersBySeasonScraper,
            "tyres/f1_tyre_manufacturers_by_season.json",
            None,
        ),
    ]

    for scraper_cls, json_rel, csv_rel in jobs:
        print(f"[list] running  {scraper_cls.__name__}")
        run_and_export(scraper_cls, json_rel, csv_rel, run_config=run_config)
        print(f"[list] finished {scraper_cls.__name__}")

    # F1SponsorshipLiveriesScraper uses a Gemini-backed ParenClassifier that must be
    # passed explicitly.  We try to load the key file; if it is absent we fall back
    # gracefully (no classification, no crash).
    try:
        _gemini_client = GeminiClient.from_key_file()
        _classifier: ParenClassifier | None = ParenClassifier(_gemini_client)
        print(
            "[main] Gemini ParenClassifier załadowany - "
            "adnotacje w nawiasach będą klasyfikowane.",
        )
    except FileNotFoundError as _e:
        _classifier = None
        print(f"[main] Brak klucza Gemini API ({_e}), klasyfikacja Gemini wyłączona.")

    run_and_export(
        F1SponsorshipLiveriesScraper,
        "sponsorship_liveries/f1_sponsorship_liveries.json",
        run_config=RunConfig(
            output_dir=BASE_WIKI_DIR,
            include_urls=True,
            debug_dir=BASE_DEBUG_DIR,
            scraper_kwargs={"classifier": _classifier},
        ),
    )


def run_complete_scrapers() -> None:
    # grand prix używa standardowego eksportu do pojedynczego pliku
    run_config = RunConfig(
        output_dir=BASE_WIKI_DIR,
        include_urls=True,
        debug_dir=BASE_DEBUG_DIR,
    )

    print("[complete] running  F1CompleteGrandPrixDataExtractor")
    run_and_export(
        F1CompleteGrandPrixDataExtractor,
        "grands_prix/f1_grands_prix_extended.json",
        run_config=run_config,
    )
    print("[complete] finished F1CompleteGrandPrixDataExtractor")

    # tory, kierowcy i sezony mają własne helpery eksportu do wielu plików
    print("[complete] running  F1CompleteCircuitDataExtractor")
    export_complete_circuits(
        output_dir=BASE_WIKI_DIR / "circuits/complete_circuits",
        include_urls=True,
    )
    print("[complete] finished F1CompleteCircuitDataExtractor")

    print("[complete] running  CompleteDriverDataExtractor")
    export_complete_drivers(
        output_dir=BASE_WIKI_DIR / "drivers/complete_drivers",
        include_urls=True,
    )
    print("[complete] finished CompleteDriverDataExtractor")

    print("[complete] running  CompleteSeasonDataExtractor")
    export_complete_seasons(
        output_dir=BASE_WIKI_DIR / "seasons/complete_seasons",
        include_urls=True,
    )
    print("[complete] finished CompleteSeasonDataExtractor")

    print("[complete] running  F1CompleteEngineManufacturerDataExtractor")
    export_complete_engine_manufacturers(
        output_dir=BASE_WIKI_DIR / "engines/complete_engine_manufacturers",
        include_urls=True,
    )
    print("[complete] finished F1CompleteEngineManufacturerDataExtractor")
    print("[complete] running  CompleteConstructorsDataExtractor")
    export_complete_constructors(
        output_dir=BASE_WIKI_DIR / "constructors/complete_constructors",
        include_urls=True,
    )
    print("[complete] finished CompleteConstructorsDataExtractor")


def main() -> None:
    # Najpierw wszystkie listy, potem komplety
    run_list_scrapers()
    run_complete_scrapers()


if __name__ == "__main__":
    main()
