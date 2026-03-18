from __future__ import annotations

import argparse
import importlib
import inspect
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from layers.application import create_default_wiki_pipeline_application
from scrapers.base.cli_entrypoint import build_run_config
from scrapers.base.cli_entrypoint import build_standard_parser
from scrapers.base.cli_entrypoint import complete_extractor_base_config
from scrapers.base.cli_entrypoint import deprecated_module_base_config
from scrapers.base.run_config import RunConfig
from scrapers.base.run_profiles import LEGACY_CLI_PROFILE_NAMES
from scrapers.base.run_profiles import LegacyCliProfileName
from scrapers.base.run_profiles import get_cli_profile_defaults

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class LegacyModuleSpec:
    target: Callable[..., None]
    base_config: RunConfig
    profile: LegacyCliProfileName


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


def _circuits_specs() -> dict[str, LegacyModuleSpec]:
    return {
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
    }


def _constructors_specs() -> dict[str, LegacyModuleSpec]:
    return {
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
    }


def _drivers_specs() -> dict[str, LegacyModuleSpec]:
    return {
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
    }


def _engines_specs() -> dict[str, LegacyModuleSpec]:
    return {
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
    }


def _grands_prix_specs() -> dict[str, LegacyModuleSpec]:
    return {
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
        "scrapers.grands_prix.red_flagged_races_scraper.world_championship": LegacyModuleSpec(
            _run_and_export_target(
                "scrapers.grands_prix.red_flagged_races_scraper.world_championship:RedFlaggedWorldChampionshipRacesScraper",
                "grands_prix/f1_red_flagged_world_championship_races.json",
            ),
            RunConfig(output_dir=Path("../../data/wiki"), include_urls=True),
            "deprecated_entrypoint",
        ),
    }


def _points_specs() -> dict[str, LegacyModuleSpec]:
    return {
        "scrapers.points.sprint_qualifying_points": LegacyModuleSpec(
            _lazy_target("scrapers.points.sprint_qualifying_points:run_list_scraper"),
            deprecated_module_base_config(),
            "list_scraper",
        ),
        "scrapers.points.points_scoring_systems_history": LegacyModuleSpec(
            _lazy_target(
                "scrapers.points.points_scoring_systems_history:run_list_scraper",
            ),
            deprecated_module_base_config(),
            "list_scraper",
        ),
        "scrapers.points.shortened_race_points": LegacyModuleSpec(
            _lazy_target("scrapers.points.shortened_race_points:run_list_scraper"),
            deprecated_module_base_config(),
            "list_scraper",
        ),
    }


def _remaining_specs() -> dict[str, LegacyModuleSpec]:
    return {
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


def _build_legacy_module_specs() -> dict[str, LegacyModuleSpec]:
    specs: dict[str, LegacyModuleSpec] = {}
    specs.update(_circuits_specs())
    specs.update(_constructors_specs())
    specs.update(_drivers_specs())
    specs.update(_engines_specs())
    specs.update(_grands_prix_specs())
    specs.update(_points_specs())
    specs.update(_remaining_specs())
    return specs


LEGACY_MODULE_SPECS: dict[str, LegacyModuleSpec] = _build_legacy_module_specs()


def _invoke_target(target: Callable[..., None], run_config: RunConfig) -> None:
    signature = inspect.signature(target)
    if "run_config" in signature.parameters:
        target(run_config=run_config)
        return
    target()


def _legacy_profile_choices() -> tuple[LegacyCliProfileName, ...]:
    return LEGACY_CLI_PROFILE_NAMES


def _build_profile_parser(default_profile: LegacyCliProfileName) -> argparse.ArgumentParser:
    profile_parser = argparse.ArgumentParser(add_help=False)
    profile_parser.add_argument(
        "--profile",
        choices=_legacy_profile_choices(),
        default=default_profile,
    )
    return profile_parser


def _parse_legacy_args(
    argv: list[str] | None,
    default_profile: LegacyCliProfileName,
) -> tuple[argparse.Namespace, argparse.Namespace]:
    profile_parser = _build_profile_parser(default_profile)
    profile_args, remaining = profile_parser.parse_known_args(argv)

    quality_default, error_default = get_cli_profile_defaults(profile_args.profile)
    parser = build_standard_parser(
        quality_report_default=quality_default,
        error_report_default=error_default,
    )
    args = parser.parse_args(remaining)
    return profile_args, args


def run_legacy_wrapper(module_path: str, argv: list[str] | None = None) -> None:
    spec = LEGACY_MODULE_SPECS[module_path]
    _, args = _parse_legacy_args(argv, spec.profile)
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


def _build_wiki_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Canonical wiki pipeline launcher")
    parser.add_argument(
        "--mode",
        choices=("layer0", "layer1", "full"),
        default="layer0",
    )
    return parser


def run_wiki_cli(argv: list[str] | None = None) -> None:
    parser = _build_wiki_parser()
    args = parser.parse_args(argv)

    app = create_default_wiki_pipeline_application(
        base_wiki_dir=Path("data/wiki").resolve(),
        base_debug_dir=Path("data/debug").resolve(),
    )
    if args.mode in {"layer0", "full"}:
        app.run_layer_zero()
    if args.mode in {"layer1", "full"}:
        app.run_layer_one()


def _build_main_parser() -> argparse.ArgumentParser:
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
    return parser


def _normalize_passthrough_args(args: list[str]) -> list[str]:
    if args and args[0] == "--":
        return args[1:]
    return args


def main(argv: list[str] | None = None) -> None:
    parser = _build_main_parser()
    args = parser.parse_args(argv)
    if args.command == "wiki":
        run_wiki_cli(["--mode", args.mode])
        return

    run_legacy_wrapper(args.module, _normalize_passthrough_args(args.args))


if __name__ == "__main__":
    main()
