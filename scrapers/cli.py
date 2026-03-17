from __future__ import annotations

import argparse
import importlib
import inspect
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.base.cli_entrypoint import CliMainProfile
from scrapers.base.cli_entrypoint import build_run_config
from scrapers.base.cli_entrypoint import build_standard_parser
from scrapers.base.cli_entrypoint import complete_extractor_base_config
from scrapers.base.cli_entrypoint import deprecated_module_base_config
from scrapers.base.run_config import RunConfig
from scrapers.wiki.application import create_default_wiki_pipeline_application

if TYPE_CHECKING:
    from collections.abc import Callable

_PROFILE_DEFAULTS: dict[CliMainProfile, tuple[bool, bool]] = {
    "list_scraper": (True, False),
    "complete_extractor": (False, False),
    "deprecated_entrypoint": (True, False),
}


@dataclass(frozen=True)
class LegacyModuleSpec:
    target: Callable[..., None]
    base_config: RunConfig
    profile: CliMainProfile


def _import_target(path: str) -> Callable[..., None]:
    module_name, attr_name = path.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    return getattr(module, attr_name)


def _lazy_target(path: str) -> Callable[..., None]:
    def _target(*args: object, **kwargs: object) -> None:
        target = _import_target(path)
        target(*args, **kwargs)

    return _target


def _run_and_export_target(
    class_path: str,
    output_json: str,
    output_csv: str | None = None,
) -> Callable[..., None]:
    def _target(*, run_config: RunConfig) -> None:
        scraper_cls = _import_target(class_path)
        run_and_export = _import_target("scrapers.base.helpers.runner:run_and_export")
        if output_csv:
            run_and_export(scraper_cls, output_json, output_csv, run_config=run_config)
            return
        run_and_export(scraper_cls, output_json, run_config=run_config)

    return _target


def _run_export_complete(
    path: str,
    output_dir: str,
    *,
    include_urls: bool = True,
) -> Callable[..., None]:
    def _target() -> None:
        export_fn = _import_target(path)
        export_fn(output_dir=Path(output_dir), include_urls=include_urls)

    return _target


LEGACY_MODULE_SPECS: dict[str, LegacyModuleSpec] = {
    "scrapers.circuits.list_scraper": LegacyModuleSpec(
        _lazy_target("scrapers.circuits.entrypoint:run_list_scraper"),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.circuits.complete_scraper": LegacyModuleSpec(
        _run_export_complete(
            "scrapers.circuits.helpers.export:export_complete_circuits",
            "../../data/wiki/circuits/complete_circuits",
        ),
        complete_extractor_base_config(),
        "complete_extractor",
    ),
    "scrapers.constructors.current_constructors_list": LegacyModuleSpec(
        _lazy_target("scrapers.constructors.entrypoint:run_list_scraper"),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.constructors.former_constructors_list": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.constructors.former_constructors_list:FormerConstructorsListScraper",
            "constructors/f1_former_constructors.json",
            "constructors/f1_former_constructors.csv",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.constructors.indianapolis_only_constructors_list": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.constructors.indianapolis_only_constructors_list:IndianapolisOnlyConstructorsListScraper",
            "constructors/f1_indianapolis_only_constructors.json",
            "constructors/f1_indianapolis_only_constructors.csv",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.constructors.privateer_teams_list": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.constructors.privateer_teams_list:PrivateerTeamsListScraper",
            "constructors/f1_privateer_teams.json",
            "constructors/f1_privateer_teams.csv",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.constructors.complete_scraper": LegacyModuleSpec(
        _run_export_complete(
            "scrapers.constructors.helpers.export:export_complete_constructors",
            "../../data/wiki/constructors/complete_constructors",
        ),
        RunConfig(),
        "complete_extractor",
    ),
    "scrapers.drivers.list_scraper": LegacyModuleSpec(
        _lazy_target("scrapers.drivers.entrypoint:run_list_scraper"),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.drivers.female_drivers_list": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.drivers.female_drivers_list:FemaleDriversListScraper",
            "drivers/female_drivers.json",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.drivers.fatalities_list_scraper": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.drivers.fatalities_list_scraper:F1FatalitiesListScraper",
            "drivers/f1_driver_fatalities.json",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.drivers.complete_scraper": LegacyModuleSpec(
        _run_export_complete(
            "scrapers.drivers.helpers.export:export_complete_drivers",
            "../../data/wiki/drivers/complete_drivers",
        ),
        RunConfig(),
        "complete_extractor",
    ),
    "scrapers.engines.engine_manufacturers_list": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.engines.engine_manufacturers_list:EngineManufacturersListScraper",
            "engines/f1_engine_manufacturers.json",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.engines.indianapolis_only_engine_manufacturers_list": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.engines.indianapolis_only_engine_manufacturers_list:IndianapolisOnlyEngineManufacturersListScraper",
            "engines/f1_engine_manufacturers_indianapolis_only.json",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.engines.engine_regulation": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.engines.engine_regulation:EngineRegulationScraper",
            "engines/f1_engine_regulations.json",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.engines.engine_restrictions": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.engines.engine_restrictions:EngineRestrictionsScraper",
            "engines/f1_engine_restrictions.json",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.engines.complete_scraper": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.engines.complete_scraper:F1CompleteEngineManufacturerDataExtractor",
            "engines/f1_engine_manufacturers_complete.json",
        ),
        RunConfig(output_dir=Path("../../data/wiki")),
        "complete_extractor",
    ),
    "scrapers.grands_prix.list_scraper": LegacyModuleSpec(
        _lazy_target("scrapers.grands_prix.entrypoint:run_list_scraper"),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.grands_prix.complete_scraper": LegacyModuleSpec(
        _lazy_target("scrapers.grands_prix.entrypoint:run_complete_scraper"),
        complete_extractor_base_config(),
        "complete_extractor",
    ),
    "scrapers.grands_prix.red_flagged_races_scraper.non_championship": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.grands_prix.red_flagged_races_scraper.non_championship:RedFlaggedNonChampionshipRacesScraper",
            "grands_prix/f1_red_flagged_non_championship_races.json",
        ),
        RunConfig(output_dir=Path("../../data/wiki"), include_urls=True),
        "deprecated_entrypoint",
    ),
    "scrapers.grands_prix.red_flagged_races_scraper.world_championship": (
        LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.grands_prix.red_flagged_races_scraper.world_championship:RedFlaggedWorldChampionshipRacesScraper",
            "grands_prix/f1_red_flagged_world_championship_races.json",
        ),
        RunConfig(output_dir=Path("../../data/wiki"), include_urls=True),
        "deprecated_entrypoint",
        )
    ),
    "scrapers.points.sprint_qualifying_points": LegacyModuleSpec(
        _lazy_target("scrapers.points.sprint_qualifying_points:run_list_scraper"),
        deprecated_module_base_config(),
        "list_scraper",
    ),
    "scrapers.points.points_scoring_systems_history": LegacyModuleSpec(
        _lazy_target("scrapers.points.points_scoring_systems_history:run_list_scraper"),
        deprecated_module_base_config(),
        "list_scraper",
    ),
    "scrapers.points.shortened_race_points": LegacyModuleSpec(
        _lazy_target("scrapers.points.shortened_race_points:run_list_scraper"),
        deprecated_module_base_config(),
        "list_scraper",
    ),
    "scrapers.seasons.list_scraper": LegacyModuleSpec(
        _lazy_target("scrapers.seasons.entrypoint:run_list_scraper"),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.seasons.complete_scraper": LegacyModuleSpec(
        _run_export_complete(
            "scrapers.seasons.helpers:export_complete_seasons",
            "../../data/wiki/seasons/complete_seasons",
        ),
        complete_extractor_base_config(),
        "complete_extractor",
    ),
    "scrapers.sponsorship_liveries.scraper": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.sponsorship_liveries.scraper:SponsorshipAndLiveriesScraper",
            "f1_sponsorship_and_livery.json",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
    "scrapers.tyres.list_scraper": LegacyModuleSpec(
        _run_and_export_target(
            "scrapers.tyres.list_scraper:TyresListScraper",
            "f1_tyre_manufacturers.json",
        ),
        deprecated_module_base_config(),
        "deprecated_entrypoint",
    ),
}


def _invoke_target(target: Callable[..., None], run_config: RunConfig) -> None:
    signature = inspect.signature(target)
    if "run_config" in signature.parameters:
        target(run_config=run_config)
        return
    target()


def run_legacy_wrapper(module_path: str, argv: list[str] | None = None) -> None:
    spec = LEGACY_MODULE_SPECS[module_path]
    profile_parser = argparse.ArgumentParser(add_help=False)
    profile_parser.add_argument(
        "--profile",
        choices=tuple(_PROFILE_DEFAULTS),
        default=spec.profile,
    )
    profile_args, remaining = profile_parser.parse_known_args(argv)

    quality_default, error_default = _PROFILE_DEFAULTS[profile_args.profile]
    parser = build_standard_parser(
        quality_report_default=quality_default,
        error_report_default=error_default,
    )
    args = parser.parse_args(remaining)
    run_config = build_run_config(base_config=spec.base_config, args=args)

    warnings.warn(
        (
            f"{module_path} is deprecated as standalone CLI; "
            f"use `python -m scrapers.cli run {module_path}`."
        ),
        DeprecationWarning,
        stacklevel=2,
    )
    _invoke_target(spec.target, run_config)


def run_wiki_cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Canonical wiki pipeline launcher")
    parser.add_argument(
        "--mode",
        choices=("layer0", "layer1", "full"),
        default="layer0",
    )
    args = parser.parse_args(argv)

    app = create_default_wiki_pipeline_application(
        base_wiki_dir=Path("data/wiki").resolve(),
        base_debug_dir=Path("data/debug").resolve(),
    )
    if args.mode in {"layer0", "full"}:
        app.run_layer_zero()
    if args.mode in {"layer1", "full"}:
        app.run_layer_one()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Canonical scrapers launcher")
    subparsers = parser.add_subparsers(dest="command", required=True)

    wiki_parser = subparsers.add_parser("wiki")
    wiki_parser.add_argument(
        "--mode",
        choices=("layer0", "layer1", "full"),
        default="layer0",
    )

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("module", choices=tuple(sorted(LEGACY_MODULE_SPECS.keys())))
    run_parser.add_argument("args", nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)
    if args.command == "wiki":
        run_wiki_cli(["--mode", args.mode])
        return

    passthrough_args = args.args
    if passthrough_args and passthrough_args[0] == "--":
        passthrough_args = passthrough_args[1:]
    run_legacy_wrapper(args.module, passthrough_args)


if __name__ == "__main__":
    main()
