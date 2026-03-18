from __future__ import annotations

import argparse
import importlib
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Protocol

from layers.application import create_default_wiki_pipeline_application
from scrapers.base.cli_entrypoint import CliMainProfile
from scrapers.base.cli_entrypoint import build_run_config
from scrapers.base.cli_entrypoint import build_standard_parser
from scrapers.base.cli_entrypoint import complete_extractor_base_config
from scrapers.base.cli_entrypoint import deprecated_module_base_config
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.circuits.entrypoint import run_list_scraper as run_circuits_list_scraper
from scrapers.circuits.helpers.export import export_complete_circuits
from scrapers.constructors.entrypoint import (
    run_list_scraper as run_constructors_list_scraper,
)
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.helpers.export import export_complete_constructors
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.drivers.entrypoint import run_list_scraper as run_drivers_list_scraper
from scrapers.drivers.fatalities_list_scraper import F1FatalitiesListScraper
from scrapers.drivers.female_drivers_list import FemaleDriversListScraper
from scrapers.drivers.helpers.export import export_complete_drivers
from scrapers.engines.complete_scraper import F1CompleteEngineManufacturerDataExtractor
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.engine_regulation import EngineRegulationScraper
from scrapers.engines.engine_restrictions import EngineRestrictionsScraper
from scrapers.engines.indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor
from scrapers.grands_prix.entrypoint import (
    run_list_scraper as run_grands_prix_list_scraper,
)
from scrapers.grands_prix.red_flagged_races_scraper.non_championship import (
    RedFlaggedNonChampionshipRacesScraper,
)
from scrapers.grands_prix.red_flagged_races_scraper.world_championship import (
    RedFlaggedWorldChampionshipRacesScraper,
)
from scrapers.points.points_scoring_systems_history import (
    run_list_scraper as run_points_scoring_systems_history_scraper,
)
from scrapers.points.shortened_race_points import (
    run_list_scraper as run_shortened_race_points_scraper,
)
from scrapers.points.sprint_qualifying_points import (
    run_list_scraper as run_sprint_qualifying_points_scraper,
)
from scrapers.seasons.entrypoint import run_list_scraper as run_seasons_list_scraper
from scrapers.seasons.helpers import export_complete_seasons
from scrapers.sponsorship_liveries.scraper import F1SponsorshipLiveriesScraper
from scrapers.tyres.list_scraper import TyreManufacturersBySeasonScraper

if TYPE_CHECKING:
    from collections.abc import Callable

    from scrapers.base.abc import ABCScraper

    CompleteExportFn = Callable[..., None]
    ZeroArgTarget = Callable[[], None]
    RunConfigTarget = Callable[..., None]

_PROFILE_DEFAULTS: dict[CliMainProfile, tuple[bool, bool]] = {
    "list_scraper": (True, False),
    "complete_extractor": (False, False),
    "deprecated_entrypoint": (True, False),
}


class CliCommandTarget(Protocol):
    def invoke(self, run_config: RunConfig) -> None:
        ...


@dataclass(frozen=True)
class CallableCliTarget:
    target: RunConfigTarget

    def invoke(self, run_config: RunConfig) -> None:
        self.target(run_config=run_config)


@dataclass(frozen=True)
class ZeroArgCliTarget:
    target: ZeroArgTarget

    def invoke(self, _run_config: RunConfig) -> None:
        self.target()


@dataclass(frozen=True)
class RunAndExportCliTarget:
    scraper_cls: type[ABCScraper]
    output_json: str
    output_csv: str | None = None
    supports_urls: bool = True

    def invoke(self, run_config: RunConfig) -> None:
        run_and_export(
            self.scraper_cls,
            self.output_json,
            self.output_csv,
            run_config=run_config,
            supports_urls=self.supports_urls,
        )


@dataclass(frozen=True)
class CompleteExportCliTarget:
    export_fn: CompleteExportFn
    output_dir: Path
    include_urls: bool = True

    def invoke(self, _run_config: RunConfig) -> None:
        self.export_fn(output_dir=self.output_dir, include_urls=self.include_urls)


@dataclass(frozen=True)
class LazyImportCliTarget:
    import_path: str

    def invoke(self, run_config: RunConfig) -> None:
        module_name, attr_name = self.import_path.split(":", maxsplit=1)
        module = importlib.import_module(module_name)
        target = getattr(module, attr_name)
        CallableCliTarget(target).invoke(run_config)


@dataclass(frozen=True)
class CliCommandSpec:
    module_path: str
    target: CliCommandTarget
    base_config: RunConfig
    profile: CliMainProfile


def _circuits_specs() -> dict[str, CliCommandSpec]:
    return {
        "scrapers.circuits.list_scraper": CliCommandSpec(
            module_path="scrapers.circuits.list_scraper",
            target=CallableCliTarget(run_circuits_list_scraper),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.circuits.complete_scraper": CliCommandSpec(
            module_path="scrapers.circuits.complete_scraper",
            target=CompleteExportCliTarget(
                export_fn=export_complete_circuits,
                output_dir=Path("../../data/wiki/circuits/complete_circuits"),
            ),
            base_config=complete_extractor_base_config(),
            profile="complete_extractor",
        ),
    }


def _constructors_specs() -> dict[str, CliCommandSpec]:
    return {
        "scrapers.constructors.current_constructors_list": CliCommandSpec(
            module_path="scrapers.constructors.current_constructors_list",
            target=CallableCliTarget(run_constructors_list_scraper),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.constructors.former_constructors_list": CliCommandSpec(
            module_path="scrapers.constructors.former_constructors_list",
            target=RunAndExportCliTarget(
                scraper_cls=FormerConstructorsListScraper,
                output_json="constructors/f1_former_constructors.json",
                output_csv="constructors/f1_former_constructors.csv",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.constructors.indianapolis_only_constructors_list": CliCommandSpec(
            module_path="scrapers.constructors.indianapolis_only_constructors_list",
            target=RunAndExportCliTarget(
                scraper_cls=IndianapolisOnlyConstructorsListScraper,
                output_json="constructors/f1_indianapolis_only_constructors.json",
                output_csv="constructors/f1_indianapolis_only_constructors.csv",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.constructors.privateer_teams_list": CliCommandSpec(
            module_path="scrapers.constructors.privateer_teams_list",
            target=RunAndExportCliTarget(
                scraper_cls=PrivateerTeamsListScraper,
                output_json="constructors/f1_privateer_teams.json",
                output_csv="constructors/f1_privateer_teams.csv",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.constructors.complete_scraper": CliCommandSpec(
            module_path="scrapers.constructors.complete_scraper",
            target=CompleteExportCliTarget(
                export_fn=export_complete_constructors,
                output_dir=Path("../../data/wiki/constructors/complete_constructors"),
            ),
            base_config=RunConfig(),
            profile="complete_extractor",
        ),
    }


def _drivers_specs() -> dict[str, CliCommandSpec]:
    return {
        "scrapers.drivers.list_scraper": CliCommandSpec(
            module_path="scrapers.drivers.list_scraper",
            target=CallableCliTarget(run_drivers_list_scraper),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.drivers.female_drivers_list": CliCommandSpec(
            module_path="scrapers.drivers.female_drivers_list",
            target=RunAndExportCliTarget(
                scraper_cls=FemaleDriversListScraper,
                output_json="drivers/female_drivers.json",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.drivers.fatalities_list_scraper": CliCommandSpec(
            module_path="scrapers.drivers.fatalities_list_scraper",
            target=RunAndExportCliTarget(
                scraper_cls=F1FatalitiesListScraper,
                output_json="drivers/f1_driver_fatalities.json",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.drivers.complete_scraper": CliCommandSpec(
            module_path="scrapers.drivers.complete_scraper",
            target=CompleteExportCliTarget(
                export_fn=export_complete_drivers,
                output_dir=Path("../../data/wiki/drivers/complete_drivers"),
            ),
            base_config=RunConfig(),
            profile="complete_extractor",
        ),
    }


def _engines_specs() -> dict[str, CliCommandSpec]:
    return {
        "scrapers.engines.engine_manufacturers_list": CliCommandSpec(
            module_path="scrapers.engines.engine_manufacturers_list",
            target=RunAndExportCliTarget(
                scraper_cls=EngineManufacturersListScraper,
                output_json="engines/f1_engine_manufacturers.json",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.engines.indianapolis_only_engine_manufacturers_list": CliCommandSpec(
            module_path="scrapers.engines.indianapolis_only_engine_manufacturers_list",
            target=RunAndExportCliTarget(
                scraper_cls=IndianapolisOnlyEngineManufacturersListScraper,
                output_json="engines/f1_engine_manufacturers_indianapolis_only.json",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.engines.engine_regulation": CliCommandSpec(
            module_path="scrapers.engines.engine_regulation",
            target=RunAndExportCliTarget(
                scraper_cls=EngineRegulationScraper,
                output_json="engines/f1_engine_regulations.json",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.engines.engine_restrictions": CliCommandSpec(
            module_path="scrapers.engines.engine_restrictions",
            target=RunAndExportCliTarget(
                scraper_cls=EngineRestrictionsScraper,
                output_json="engines/f1_engine_restrictions.json",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.engines.complete_scraper": CliCommandSpec(
            module_path="scrapers.engines.complete_scraper",
            target=RunAndExportCliTarget(
                scraper_cls=F1CompleteEngineManufacturerDataExtractor,
                output_json="engines/f1_engine_manufacturers_complete.json",
            ),
            base_config=RunConfig(output_dir=Path("../../data/wiki")),
            profile="complete_extractor",
        ),
    }


def _grands_prix_specs() -> dict[str, CliCommandSpec]:
    grands_prix_report_config = RunConfig(
        output_dir=Path("../../data/wiki"),
        include_urls=True,
    )
    return {
        "scrapers.grands_prix.list_scraper": CliCommandSpec(
            module_path="scrapers.grands_prix.list_scraper",
            target=CallableCliTarget(run_grands_prix_list_scraper),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.grands_prix.complete_scraper": CliCommandSpec(
            module_path="scrapers.grands_prix.complete_scraper",
            target=RunAndExportCliTarget(
                scraper_cls=F1CompleteGrandPrixDataExtractor,
                output_json="raw/grands_prix/seeds/f1_grands_prix_extended.json",
            ),
            base_config=complete_extractor_base_config(),
            profile="complete_extractor",
        ),
        (
            "scrapers.grands_prix.red_flagged_races_scraper.non_championship"
        ): CliCommandSpec(
            module_path="scrapers.grands_prix.red_flagged_races_scraper.non_championship",
            target=RunAndExportCliTarget(
                scraper_cls=RedFlaggedNonChampionshipRacesScraper,
                output_json="grands_prix/f1_red_flagged_non_championship_races.json",
            ),
            base_config=grands_prix_report_config,
            profile="deprecated_entrypoint",
        ),
        (
            "scrapers.grands_prix.red_flagged_races_scraper.world_championship"
        ): CliCommandSpec(
            module_path="scrapers.grands_prix.red_flagged_races_scraper.world_championship",
            target=RunAndExportCliTarget(
                scraper_cls=RedFlaggedWorldChampionshipRacesScraper,
                output_json="grands_prix/f1_red_flagged_world_championship_races.json",
            ),
            base_config=grands_prix_report_config,
            profile="deprecated_entrypoint",
        ),
    }


def _points_specs() -> dict[str, CliCommandSpec]:
    return {
        "scrapers.points.sprint_qualifying_points": CliCommandSpec(
            module_path="scrapers.points.sprint_qualifying_points",
            target=CallableCliTarget(run_sprint_qualifying_points_scraper),
            base_config=deprecated_module_base_config(),
            profile="list_scraper",
        ),
        "scrapers.points.points_scoring_systems_history": CliCommandSpec(
            module_path="scrapers.points.points_scoring_systems_history",
            target=CallableCliTarget(run_points_scoring_systems_history_scraper),
            base_config=deprecated_module_base_config(),
            profile="list_scraper",
        ),
        "scrapers.points.shortened_race_points": CliCommandSpec(
            module_path="scrapers.points.shortened_race_points",
            target=CallableCliTarget(run_shortened_race_points_scraper),
            base_config=deprecated_module_base_config(),
            profile="list_scraper",
        ),
    }


def _remaining_specs() -> dict[str, CliCommandSpec]:
    return {
        "scrapers.seasons.list_scraper": CliCommandSpec(
            module_path="scrapers.seasons.list_scraper",
            target=CallableCliTarget(run_seasons_list_scraper),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.seasons.complete_scraper": CliCommandSpec(
            module_path="scrapers.seasons.complete_scraper",
            target=CompleteExportCliTarget(
                export_fn=export_complete_seasons,
                output_dir=Path("../../data/wiki/seasons/complete_seasons"),
            ),
            base_config=complete_extractor_base_config(),
            profile="complete_extractor",
        ),
        "scrapers.sponsorship_liveries.scraper": CliCommandSpec(
            module_path="scrapers.sponsorship_liveries.scraper",
            target=RunAndExportCliTarget(
                scraper_cls=F1SponsorshipLiveriesScraper,
                output_json="f1_sponsorship_and_livery.json",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
        "scrapers.tyres.list_scraper": CliCommandSpec(
            module_path="scrapers.tyres.list_scraper",
            target=RunAndExportCliTarget(
                scraper_cls=TyreManufacturersBySeasonScraper,
                output_json="f1_tyre_manufacturers.json",
            ),
            base_config=deprecated_module_base_config(),
            profile="deprecated_entrypoint",
        ),
    }


def _build_legacy_module_specs() -> dict[str, CliCommandSpec]:
    specs: dict[str, CliCommandSpec] = {}
    specs.update(_circuits_specs())
    specs.update(_constructors_specs())
    specs.update(_drivers_specs())
    specs.update(_engines_specs())
    specs.update(_grands_prix_specs())
    specs.update(_points_specs())
    specs.update(_remaining_specs())
    return specs


LEGACY_MODULE_SPECS: dict[str, CliCommandSpec] = _build_legacy_module_specs()


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
    spec.target.invoke(run_config)


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
