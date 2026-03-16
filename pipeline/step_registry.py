from __future__ import annotations

from datetime import datetime
from datetime import timezone
from importlib import import_module
from pathlib import Path

from pipeline.orchestrator import Layer0Step
from pipeline.orchestrator import Layer1Step
from pipeline.orchestrator import PipelineStep

BASE_WIKI_DIR = Path("data/wiki").resolve()
BASE_DEBUG_DIR = Path("data/debug").resolve()
CURRENT_YEAR = datetime.now(tz=timezone.utc).year


def _load_attr(module_path: str, attr_name: str):
    module = import_module(module_path)
    return getattr(module, attr_name)


def _base_run_config():
    run_config_cls = _load_attr("scrapers.base.run_config", "RunConfig")
    return run_config_cls(
        output_dir=BASE_WIKI_DIR,
        include_urls=True,
        debug_dir=BASE_DEBUG_DIR,
    )


def _run_and_export(
    scraper_cls: object,
    json_rel: str,
    csv_rel: str | None = None,
) -> None:
    run_and_export = _load_attr("scrapers.base.helpers.runner", "run_and_export")
    run_and_export(scraper_cls, json_rel, csv_rel, run_config=_base_run_config())


def _list_step(
    step_id: str,
    scraper_module: str,
    scraper_name: str,
    json_rel: str,
) -> Layer0Step:
    def _runner() -> None:
        scraper_cls = _load_attr(scraper_module, scraper_name)
        print(f"[layer0] running  {scraper_name}")
        _run_and_export(scraper_cls, json_rel)
        print(f"[layer0] finished {scraper_name}")

    return Layer0Step(
        step_id=step_id,
        input_source="wikipedia",
        parser=scraper_name,
        output_path=str(BASE_WIKI_DIR / json_rel),
        runner=_runner,
    )


def _sponsorship_step() -> Layer0Step:
    def _runner() -> None:
        gemini_client_cls = _load_attr("infrastructure.gemini.client", "GeminiClient")
        classifier_cls = _load_attr(
            "scrapers.sponsorship_liveries.helpers.paren_classifier",
            "ParenClassifier",
        )
        run_config_cls = _load_attr("scrapers.base.run_config", "RunConfig")
        scraper_cls = _load_attr(
            "scrapers.sponsorship_liveries.scraper",
            "F1SponsorshipLiveriesScraper",
        )
        run_and_export = _load_attr("scrapers.base.helpers.runner", "run_and_export")

        print("[layer0] running  F1SponsorshipLiveriesScraper")
        try:
            gemini_client = gemini_client_cls.from_key_file()
            classifier = classifier_cls(gemini_client)
            print(
                "[main] Gemini ParenClassifier załadowany - "
                "adnotacje w nawiasach będą klasyfikowane.",
            )
        except FileNotFoundError as exc:
            classifier = None
            print(
                f"[main] Brak klucza Gemini API ({exc}), "
                "klasyfikacja Gemini wyłączona.",
            )

        run_and_export(
            scraper_cls,
            "sponsorship_liveries/f1_sponsorship_liveries.json",
            run_config=run_config_cls(
                output_dir=BASE_WIKI_DIR,
                include_urls=True,
                debug_dir=BASE_DEBUG_DIR,
                scraper_kwargs={"classifier": classifier},
            ),
        )
        print("[layer0] finished F1SponsorshipLiveriesScraper")

    output = BASE_WIKI_DIR / "sponsorship_liveries/f1_sponsorship_liveries.json"
    return Layer0Step(
        step_id="layer0_sponsorship_liveries",
        input_source="wikipedia",
        parser="F1SponsorshipLiveriesScraper",
        output_path=str(output),
        runner=_runner,
    )


def _complete_step(
    step_id: str,
    parser: str,
    output_path: Path,
    exporter_loader,
) -> Layer1Step:
    def _runner() -> None:
        print(f"[layer1] running  {parser}")
        exporter_loader()(output_dir=output_path, include_urls=True)
        print(f"[layer1] finished {parser}")

    return Layer1Step(
        step_id=step_id,
        input_source="wikipedia",
        parser=parser,
        output_path=str(output_path),
        runner=_runner,
    )


def _complete_grand_prix_step() -> Layer1Step:
    json_rel = "grands_prix/f1_grands_prix_extended.json"

    def _runner() -> None:
        scraper_cls = _load_attr(
            "scrapers.grands_prix.complete_scraper",
            "F1CompleteGrandPrixDataExtractor",
        )
        print("[layer1] running  F1CompleteGrandPrixDataExtractor")
        _run_and_export(scraper_cls, json_rel)
        print("[layer1] finished F1CompleteGrandPrixDataExtractor")

    return Layer1Step(
        step_id="layer1_complete_grand_prix",
        input_source="wikipedia",
        parser="F1CompleteGrandPrixDataExtractor",
        output_path=str(BASE_WIKI_DIR / json_rel),
        runner=_runner,
    )


def get_layer0_steps() -> list[Layer0Step]:
    specs = [
        (
            "layer0_circuits",
            "scrapers.circuits.list_scraper",
            "CircuitsListScraper",
            "circuits/f1_circuits.json",
        ),
        (
            "layer0_constructors_current",
            "scrapers.constructors.current_constructors_list",
            "CurrentConstructorsListScraper",
            f"constructors/f1_constructors_{CURRENT_YEAR}.json",
        ),
        (
            "layer0_constructors_former",
            "scrapers.constructors.former_constructors_list",
            "FormerConstructorsListScraper",
            "constructors/f1_former_constructors.json",
        ),
        (
            "layer0_constructors_indianapolis_only",
            "scrapers.constructors.indianapolis_only_constructors_list",
            "IndianapolisOnlyConstructorsListScraper",
            "constructors/f1_indianapolis_only_constructors.json",
        ),
        (
            "layer0_constructors_privateer",
            "scrapers.constructors.privateer_teams_list",
            "PrivateerTeamsListScraper",
            "constructors/f1_privateer_teams.json",
        ),
        (
            "layer0_drivers",
            "scrapers.drivers.list_scraper",
            "F1DriversListScraper",
            "drivers/f1_drivers.json",
        ),
        (
            "layer0_drivers_female",
            "scrapers.drivers.female_drivers_list",
            "FemaleDriversListScraper",
            "drivers/female_drivers.json",
        ),
        (
            "layer0_drivers_fatalities",
            "scrapers.drivers.fatalities_list_scraper",
            "F1FatalitiesListScraper",
            "drivers/f1_driver_fatalities.json",
        ),
        (
            "layer0_engines_indianapolis_only",
            "scrapers.engines.indianapolis_only_engine_manufacturers_list",
            "IndianapolisOnlyEngineManufacturersListScraper",
            "engines/f1_indianapolis_only_engine_manufacturers.json",
        ),
        (
            "layer0_engines_restrictions",
            "scrapers.engines.engine_restrictions",
            "EngineRestrictionsScraper",
            "engines/f1_engine_restrictions.json",
        ),
        (
            "layer0_engines_regulations",
            "scrapers.engines.engine_regulation",
            "EngineRegulationScraper",
            "engines/f1_engine_regulations.json",
        ),
        (
            "layer0_engines_manufacturers",
            "scrapers.engines.engine_manufacturers_list",
            "EngineManufacturersListScraper",
            "engines/f1_engine_manufacturers.json",
        ),
        (
            "layer0_red_flagged_wc",
            "scrapers.grands_prix.red_flagged_races_scraper.world_championship",
            "RedFlaggedWorldChampionshipRacesScraper",
            "grands_prix/f1_red_flagged_world_championship_races.json",
        ),
        (
            "layer0_red_flagged_non_wc",
            "scrapers.grands_prix.red_flagged_races_scraper.non_championship",
            "RedFlaggedNonChampionshipRacesScraper",
            "grands_prix/f1_red_flagged_non_championship_races.json",
        ),
        (
            "layer0_points_sprint",
            "scrapers.points.sprint_qualifying_points",
            "SprintQualifyingPointsScraper",
            "points/points_scoring_systems_sprint.json",
        ),
        (
            "layer0_points_shortened",
            "scrapers.points.shortened_race_points",
            "ShortenedRacePointsScraper",
            "points/points_scoring_systems_shortened.json",
        ),
        (
            "layer0_points_history",
            "scrapers.points.points_scoring_systems_history",
            "PointsScoringSystemsHistoryScraper",
            "points/points_scoring_systems_history.json",
        ),
        (
            "layer0_tyres",
            "scrapers.tyres.list_scraper",
            "TyreManufacturersBySeasonScraper",
            "tyres/f1_tyre_manufacturers_by_season.json",
        ),
    ]
    steps = [_list_step(*spec) for spec in specs]
    return [*steps, _sponsorship_step()]


def get_layer1_steps() -> list[Layer1Step]:
    return [
        _complete_grand_prix_step(),
        _complete_step(
            "layer1_complete_circuits",
            "F1CompleteCircuitDataExtractor",
            BASE_WIKI_DIR / "circuits/complete_circuits",
            lambda: _load_attr(
                "scrapers.circuits.helpers.export",
                "export_complete_circuits",
            ),
        ),
        _complete_step(
            "layer1_complete_drivers",
            "CompleteDriverDataExtractor",
            BASE_WIKI_DIR / "drivers/complete_drivers",
            lambda: _load_attr(
                "scrapers.drivers.helpers.export",
                "export_complete_drivers",
            ),
        ),
        _complete_step(
            "layer1_complete_seasons",
            "CompleteSeasonDataExtractor",
            BASE_WIKI_DIR / "seasons/complete_seasons",
            lambda: _load_attr("scrapers.seasons.helpers", "export_complete_seasons"),
        ),
        _complete_step(
            "layer1_complete_engine_manufacturers",
            "F1CompleteEngineManufacturerDataExtractor",
            BASE_WIKI_DIR / "engines/complete_engine_manufacturers",
            lambda: _load_attr(
                "scrapers.engines.helpers.export",
                "export_complete_engine_manufacturers",
            ),
        ),
        _complete_step(
            "layer1_complete_constructors",
            "CompleteConstructorsDataExtractor",
            BASE_WIKI_DIR / "constructors/complete_constructors",
            lambda: _load_attr(
                "scrapers.constructors.helpers.export",
                "export_complete_constructors",
            ),
        ),
    ]


def get_all_steps() -> list[PipelineStep]:
    return [*get_layer0_steps(), *get_layer1_steps()]
