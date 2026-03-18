from __future__ import annotations

import argparse
import dataclasses
import importlib
import inspect
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from layers.application import create_default_wiki_pipeline_application
from scrapers.base.cli_entrypoint import CliMainProfile
from scrapers.base.cli_entrypoint import build_run_config
from scrapers.base.cli_entrypoint import build_standard_parser
from scrapers.base.cli_entrypoint import complete_extractor_base_config
from scrapers.base.cli_entrypoint import deprecated_module_base_config
from scrapers.base.run_config import RunConfig

if TYPE_CHECKING:
    from collections.abc import Callable

_PROFILE_DEFAULTS: dict[CliMainProfile, tuple[bool, bool]] = {
    "list_scraper": (True, False),
    "complete_extractor": (False, False),
    "deprecated_entrypoint": (True, False),
}

BaseConfigFactory = Literal["deprecated", "complete", "default"]
LegacyTargetFactory = Literal["lazy", "run_and_export", "run_export_complete"]


@dataclass(frozen=True)
class LegacyModuleSpec:
    target: Callable[..., None]
    base_config: RunConfig
    profile: CliMainProfile


@dataclass(frozen=True)
class LegacyModuleDefinition:
    module_path: str
    factory: LegacyTargetFactory
    target_path: str
    profile: CliMainProfile
    base_config_factory: BaseConfigFactory = "deprecated"
    output_json: str | None = None
    output_csv: str | None = None
    output_dir: str | None = None
    include_urls: bool | None = None
    base_config_overrides: dict[str, object] | None = None


@dataclass(frozen=True)
class LegacyCliRegistry:
    definitions: tuple[LegacyModuleDefinition, ...]

    def build_specs(self) -> dict[str, LegacyModuleSpec]:
        return {
            definition.module_path: LegacyModuleSpec(
                target=self._build_target(definition),
                base_config=self._build_base_config(definition),
                profile=definition.profile,
            )
            for definition in self.definitions
        }

    def _build_target(self, definition: LegacyModuleDefinition) -> Callable[..., None]:
        if definition.factory == "lazy":
            return _lazy_target(definition.target_path)
        if definition.factory == "run_and_export":
            return _run_and_export_target(
                definition.target_path,
                definition.output_json,
                definition.output_csv,
            )
        return _run_export_complete(
            definition.target_path,
            definition.output_dir,
            include_urls=definition.include_urls,
        )

    def _build_base_config(self, definition: LegacyModuleDefinition) -> RunConfig:
        base_config = _build_base_config(definition.base_config_factory)
        if not definition.base_config_overrides:
            return base_config
        return dataclasses.replace(base_config, **definition.base_config_overrides)


def _build_base_config(factory: BaseConfigFactory) -> RunConfig:
    if factory == "deprecated":
        return deprecated_module_base_config()
    if factory == "complete":
        return complete_extractor_base_config()
    return RunConfig()


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
    output_json: str | None,
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
    output_dir: str | None,
    *,
    include_urls: bool | None = True,
) -> Callable[..., None]:
    def _target() -> None:
        export_fn = _import_target(path)
        export_fn(output_dir=Path(output_dir), include_urls=include_urls)

    return _target


LEGACY_MODULE_REGISTRY = LegacyCliRegistry(
    definitions=(
        LegacyModuleDefinition(
            module_path="scrapers.circuits.list_scraper",
            factory="lazy",
            target_path="scrapers.circuits.entrypoint:run_list_scraper",
            profile="deprecated_entrypoint",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.circuits.complete_scraper",
            factory="run_export_complete",
            target_path="scrapers.circuits.helpers.export:export_complete_circuits",
            profile="complete_extractor",
            base_config_factory="complete",
            output_dir="../../data/wiki/circuits/complete_circuits",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.constructors.current_constructors_list",
            factory="lazy",
            target_path="scrapers.constructors.entrypoint:run_list_scraper",
            profile="deprecated_entrypoint",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.constructors.former_constructors_list",
            factory="run_and_export",
            target_path=(
                "scrapers.constructors.former_constructors_list:"
                "FormerConstructorsListScraper"
            ),
            profile="deprecated_entrypoint",
            output_json="constructors/f1_former_constructors.json",
            output_csv="constructors/f1_former_constructors.csv",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.constructors.indianapolis_only_constructors_list",
            factory="run_and_export",
            target_path=(
                "scrapers.constructors.indianapolis_only_constructors_list:"
                "IndianapolisOnlyConstructorsListScraper"
            ),
            profile="deprecated_entrypoint",
            output_json="constructors/f1_indianapolis_only_constructors.json",
            output_csv="constructors/f1_indianapolis_only_constructors.csv",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.constructors.privateer_teams_list",
            factory="run_and_export",
            target_path="scrapers.constructors.privateer_teams_list:PrivateerTeamsListScraper",
            profile="deprecated_entrypoint",
            output_json="constructors/f1_privateer_teams.json",
            output_csv="constructors/f1_privateer_teams.csv",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.constructors.complete_scraper",
            factory="run_export_complete",
            target_path=(
                "scrapers.constructors.helpers.export:export_complete_constructors"
            ),
            profile="complete_extractor",
            base_config_factory="default",
            output_dir="../../data/wiki/constructors/complete_constructors",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.drivers.list_scraper",
            factory="lazy",
            target_path="scrapers.drivers.entrypoint:run_list_scraper",
            profile="deprecated_entrypoint",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.drivers.female_drivers_list",
            factory="run_and_export",
            target_path="scrapers.drivers.female_drivers_list:FemaleDriversListScraper",
            profile="deprecated_entrypoint",
            output_json="drivers/female_drivers.json",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.drivers.fatalities_list_scraper",
            factory="run_and_export",
            target_path="scrapers.drivers.fatalities_list_scraper:F1FatalitiesListScraper",
            profile="deprecated_entrypoint",
            output_json="drivers/f1_driver_fatalities.json",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.drivers.complete_scraper",
            factory="run_export_complete",
            target_path="scrapers.drivers.helpers.export:export_complete_drivers",
            profile="complete_extractor",
            base_config_factory="default",
            output_dir="../../data/wiki/drivers/complete_drivers",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.engines.engine_manufacturers_list",
            factory="run_and_export",
            target_path=(
                "scrapers.engines.engine_manufacturers_list:"
                "EngineManufacturersListScraper"
            ),
            profile="deprecated_entrypoint",
            output_json="engines/f1_engine_manufacturers.json",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.engines.indianapolis_only_engine_manufacturers_list",
            factory="run_and_export",
            target_path=(
                "scrapers.engines.indianapolis_only_engine_manufacturers_list:"
                "IndianapolisOnlyEngineManufacturersListScraper"
            ),
            profile="deprecated_entrypoint",
            output_json="engines/f1_engine_manufacturers_indianapolis_only.json",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.engines.engine_regulation",
            factory="run_and_export",
            target_path="scrapers.engines.engine_regulation:EngineRegulationScraper",
            profile="deprecated_entrypoint",
            output_json="engines/f1_engine_regulations.json",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.engines.engine_restrictions",
            factory="run_and_export",
            target_path="scrapers.engines.engine_restrictions:EngineRestrictionsScraper",
            profile="deprecated_entrypoint",
            output_json="engines/f1_engine_restrictions.json",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.engines.complete_scraper",
            factory="run_and_export",
            target_path=(
                "scrapers.engines.complete_scraper:"
                "F1CompleteEngineManufacturerDataExtractor"
            ),
            profile="complete_extractor",
            base_config_factory="default",
            output_json="engines/f1_engine_manufacturers_complete.json",
            base_config_overrides={"output_dir": Path("../../data/wiki")},
        ),
        LegacyModuleDefinition(
            module_path="scrapers.grands_prix.list_scraper",
            factory="lazy",
            target_path="scrapers.grands_prix.entrypoint:run_list_scraper",
            profile="deprecated_entrypoint",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.grands_prix.complete_scraper",
            factory="lazy",
            target_path="scrapers.grands_prix.entrypoint:run_complete_scraper",
            profile="complete_extractor",
            base_config_factory="complete",
        ),
        LegacyModuleDefinition(
            module_path=(
                "scrapers.grands_prix.red_flagged_races_scraper.non_championship"
            ),
            factory="run_and_export",
            target_path=(
                "scrapers.grands_prix.red_flagged_races_scraper."
                "non_championship:RedFlaggedNonChampionshipRacesScraper"
            ),
            profile="deprecated_entrypoint",
            output_json="grands_prix/f1_red_flagged_non_championship_races.json",
            base_config_overrides={
                "output_dir": Path("../../data/wiki"),
                "include_urls": True,
            },
        ),
        LegacyModuleDefinition(
            module_path=(
                "scrapers.grands_prix.red_flagged_races_scraper.world_championship"
            ),
            factory="run_and_export",
            target_path=(
                "scrapers.grands_prix.red_flagged_races_scraper."
                "world_championship:RedFlaggedWorldChampionshipRacesScraper"
            ),
            profile="deprecated_entrypoint",
            output_json="grands_prix/f1_red_flagged_world_championship_races.json",
            base_config_overrides={
                "output_dir": Path("../../data/wiki"),
                "include_urls": True,
            },
        ),
        LegacyModuleDefinition(
            module_path="scrapers.points.sprint_qualifying_points",
            factory="lazy",
            target_path="scrapers.points.sprint_qualifying_points:run_list_scraper",
            profile="list_scraper",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.points.points_scoring_systems_history",
            factory="lazy",
            target_path=(
                "scrapers.points.points_scoring_systems_history:run_list_scraper"
            ),
            profile="list_scraper",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.points.shortened_race_points",
            factory="lazy",
            target_path="scrapers.points.shortened_race_points:run_list_scraper",
            profile="list_scraper",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.seasons.list_scraper",
            factory="lazy",
            target_path="scrapers.seasons.entrypoint:run_list_scraper",
            profile="deprecated_entrypoint",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.seasons.complete_scraper",
            factory="run_export_complete",
            target_path="scrapers.seasons.helpers:export_complete_seasons",
            profile="complete_extractor",
            base_config_factory="complete",
            output_dir="../../data/wiki/seasons/complete_seasons",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.sponsorship_liveries.scraper",
            factory="run_and_export",
            target_path=(
                "scrapers.sponsorship_liveries.scraper:" "SponsorshipAndLiveriesScraper"
            ),
            profile="deprecated_entrypoint",
            output_json="f1_sponsorship_and_livery.json",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.tyres.list_scraper",
            factory="run_and_export",
            target_path="scrapers.tyres.list_scraper:TyresListScraper",
            profile="deprecated_entrypoint",
            output_json="f1_tyre_manufacturers.json",
        ),
    ),
)

LEGACY_MODULE_SPECS: dict[str, LegacyModuleSpec] = LEGACY_MODULE_REGISTRY.build_specs()


def _invoke_target(target: Callable[..., None], run_config: RunConfig) -> None:
    signature = inspect.signature(target)
    if "run_config" in signature.parameters:
        target(run_config=run_config)
        return
    target()


def _build_profile_parser(default_profile: CliMainProfile) -> argparse.ArgumentParser:
    profile_parser = argparse.ArgumentParser(add_help=False)
    profile_parser.add_argument(
        "--profile",
        choices=tuple(_PROFILE_DEFAULTS),
        default=default_profile,
    )
    return profile_parser


def _parse_legacy_args(
    argv: list[str] | None,
    default_profile: CliMainProfile,
) -> tuple[argparse.Namespace, argparse.Namespace]:
    profile_parser = _build_profile_parser(default_profile)
    profile_args, remaining = profile_parser.parse_known_args(argv)

    quality_default, error_default = _PROFILE_DEFAULTS[profile_args.profile]
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
