from __future__ import annotations

import argparse
import dataclasses
import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path

from layers.path_resolver import DEFAULT_PATH_RESOLVER
from layers.path_resolver import PathResolver
from typing import TYPE_CHECKING
from typing import Literal

from scrapers.base.cli_entrypoint import build_run_config
from scrapers.base.cli_entrypoint import build_standard_parser
from scrapers.base.cli_entrypoint import complete_extractor_base_config
from scrapers.base.cli_entrypoint import deprecated_module_base_config
from scrapers.base.domain_entrypoint import get_domain_entrypoint_scraper_metadata
from scrapers.base.logging import configure_logging
from scrapers.base.run_config import RunConfig
from scrapers.base.run_profiles import LEGACY_CLI_PROFILE_NAMES
from scrapers.base.run_profiles import LegacyCliProfileName
from scrapers.base.run_profiles import get_cli_profile_defaults
from scrapers.base.runner import ScraperRunner
from scrapers.wiki.sources_registry import ENGINES_INDIANAPOLIS_ONLY_LEGACY_SOURCE
from scrapers.wiki.sources_registry import get_source_by_list_filename
from scrapers.wiki.sources_registry import get_source_by_seed_name
from scrapers.wiki.sources_registry import resolve_list_filename
from scrapers.wiki.sources_registry import validate_sources_registry_consistency

if TYPE_CHECKING:
    from collections.abc import Callable

BaseConfigFactory = Literal["deprecated", "complete", "default"]
LegacyTargetFactory = Literal["lazy", "run_and_export", "run_export_complete"]
SCRAPER_MODULE_PATH_PARTS = 3

CLI_PATH_RESOLVER = PathResolver(
    exports_root=Path("../../data/wiki"),
    debug_root=Path("../../data/debug"),
)


@dataclass(frozen=True)
class LegacyModuleSpec:
    target: Callable[..., None]
    base_config: RunConfig
    profile: LegacyCliProfileName


@dataclass(frozen=True)
class LegacyModuleDefinition:
    module_path: str
    factory: LegacyTargetFactory
    target_path: str
    profile: LegacyCliProfileName
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


@dataclass(frozen=True)
class DomainCommand:
    name: str
    module_path: str
    scraper_path: str




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
        runner = ScraperRunner(run_config)
        if output_csv:
            runner.run_and_export(scraper_cls, output_json, output_csv)
            return
        runner.run_and_export(scraper_cls, output_json)

    return _target


def _run_export_complete(
    path: str,
    output_dir: str | None,
    *,
    include_urls: bool | None = True,
) -> Callable[..., None]:
    def _target() -> None:
        export_fn = _import_target(path)
        if output_dir is None:
            msg = "output_dir cannot be None for complete export target."
            raise ValueError(msg)
        export_fn(
            output_dir=CLI_PATH_RESOLVER.exports(output_dir),
            include_urls=include_urls,
        )

    return _target


def _list_output_path(*, seed_name: str, output_category: str | None = None) -> str:
    source = get_source_by_seed_name(seed_name, warn=False)
    category = output_category or source.output_category
    return f"{category}/{source.list_filename}"


def _legacy_alias_output_path(
    *,
    legacy_filename: str,
    output_category: str,
) -> str:
    canonical_filename = resolve_list_filename(legacy_filename, warn=False)
    source = get_source_by_list_filename(canonical_filename, warn=False)
    if source.output_category != output_category:
        msg = (
            "Legacy CLI output category mismatch for source "
            f"{legacy_filename!r}: expected {source.output_category!r}, got {output_category!r}"
        )
        raise ValueError(msg)
    return f"{output_category}/{legacy_filename}"


LEGACY_MODULE_REGISTRY = LegacyCliRegistry(
    definitions=(
        LegacyModuleDefinition(
            module_path="scrapers.circuits.list_scraper",
            factory="lazy",
            target_path="scrapers.circuits.entrypoint:run_list_scraper",
            profile="deprecated_entrypoint",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.circuits.entrypoint",
            factory="lazy",
            target_path="scrapers.circuits.entrypoint:run_list_scraper",
            profile="list_scraper",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.circuits.complete_scraper",
            factory="run_export_complete",
            target_path="scrapers.circuits.helpers.export:export_complete_circuits",
            profile="complete_extractor",
            base_config_factory="complete",
            output_dir="circuits/complete_circuits",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.constructors.current_constructors_list",
            factory="lazy",
            target_path="scrapers.constructors.entrypoint:run_list_scraper",
            profile="deprecated_entrypoint",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.constructors.entrypoint",
            factory="lazy",
            target_path="scrapers.constructors.entrypoint:run_list_scraper",
            profile="list_scraper",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.constructors.former_constructors_list",
            factory="run_and_export",
            target_path=(
                "scrapers.constructors.former_constructors_list:"
                "FormerConstructorsListScraper"
            ),
            profile="deprecated_entrypoint",
            output_json=_list_output_path(seed_name="constructors_former", output_category="constructors"),
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
            output_json=_list_output_path(seed_name="constructors_indianapolis_only", output_category="constructors"),
            output_csv="constructors/f1_indianapolis_only_constructors.csv",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.constructors.privateer_teams_list",
            factory="run_and_export",
            target_path="scrapers.constructors.privateer_teams_list:PrivateerTeamsListScraper",
            profile="deprecated_entrypoint",
            output_json=_list_output_path(seed_name="constructors_privateer", output_category="constructors"),
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
            output_dir="constructors/complete_constructors",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.drivers.list_scraper",
            factory="lazy",
            target_path="scrapers.drivers.entrypoint:run_list_scraper",
            profile="deprecated_entrypoint",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.drivers.entrypoint",
            factory="lazy",
            target_path="scrapers.drivers.entrypoint:run_list_scraper",
            profile="list_scraper",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.drivers.female_drivers_list",
            factory="run_and_export",
            target_path="scrapers.drivers.female_drivers_list:FemaleDriversListScraper",
            profile="deprecated_entrypoint",
            output_json=_list_output_path(seed_name="drivers_female"),
        ),
        LegacyModuleDefinition(
            module_path="scrapers.drivers.fatalities_list_scraper",
            factory="run_and_export",
            target_path="scrapers.drivers.fatalities_list_scraper:F1FatalitiesListScraper",
            profile="deprecated_entrypoint",
            output_json=_list_output_path(seed_name="drivers_fatalities"),
        ),
        LegacyModuleDefinition(
            module_path="scrapers.drivers.complete_scraper",
            factory="run_export_complete",
            target_path="scrapers.drivers.helpers.export:export_complete_drivers",
            profile="complete_extractor",
            base_config_factory="default",
            output_dir="drivers/complete_drivers",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.engines.engine_manufacturers_list",
            factory="run_and_export",
            target_path=(
                "scrapers.engines.engine_manufacturers_list:"
                "EngineManufacturersListScraper"
            ),
            profile="deprecated_entrypoint",
            output_json=_list_output_path(seed_name="engines_manufacturers"),
        ),
        LegacyModuleDefinition(
            module_path="scrapers.engines.indianapolis_only_engine_manufacturers_list",
            factory="run_and_export",
            target_path=(
                "scrapers.engines.indianapolis_only_engine_manufacturers_list:"
                "IndianapolisOnlyEngineManufacturersListScraper"
            ),
            profile="deprecated_entrypoint",
            output_json=_legacy_alias_output_path(legacy_filename=ENGINES_INDIANAPOLIS_ONLY_LEGACY_SOURCE, output_category="engines"),
        ),
        LegacyModuleDefinition(
            module_path="scrapers.engines.engine_regulation",
            factory="run_and_export",
            target_path="scrapers.engines.engine_regulation:EngineRegulationScraper",
            profile="deprecated_entrypoint",
            output_json=_list_output_path(seed_name="engines_regulations", output_category="engines"),
        ),
        LegacyModuleDefinition(
            module_path="scrapers.engines.engine_restrictions",
            factory="run_and_export",
            target_path="scrapers.engines.engine_restrictions:EngineRestrictionsScraper",
            profile="deprecated_entrypoint",
            output_json=_list_output_path(seed_name="engines_restrictions", output_category="engines"),
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
            base_config_overrides={"output_dir": CLI_PATH_RESOLVER.exports_root},
        ),
        LegacyModuleDefinition(
            module_path="scrapers.grands_prix.list_scraper",
            factory="lazy",
            target_path="scrapers.grands_prix.entrypoint:run_list_scraper",
            profile="deprecated_entrypoint",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.grands_prix.entrypoint",
            factory="lazy",
            target_path="scrapers.grands_prix.entrypoint:run_list_scraper",
            profile="list_scraper",
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
                "output_dir": CLI_PATH_RESOLVER.exports_root,
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
                "output_dir": CLI_PATH_RESOLVER.exports_root,
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
            module_path="scrapers.seasons.entrypoint",
            factory="lazy",
            target_path="scrapers.seasons.entrypoint:run_list_scraper",
            profile="list_scraper",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.seasons.complete_scraper",
            factory="run_export_complete",
            target_path="scrapers.seasons.helpers:export_complete_seasons",
            profile="complete_extractor",
            base_config_factory="complete",
            output_dir="seasons/complete_seasons",
        ),
        LegacyModuleDefinition(
            module_path="scrapers.sponsorship_liveries.scraper",
            factory="run_and_export",
            target_path=(
                "scrapers.sponsorship_liveries.scraper:SponsorshipAndLiveriesScraper"
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

SCRAPER_REGISTRY: dict[str, LegacyModuleSpec] = LEGACY_MODULE_REGISTRY.build_specs()
MODULE_DEFINITIONS: dict[str, LegacyModuleDefinition] = {
    definition.module_path: definition
    for definition in LEGACY_MODULE_REGISTRY.definitions
}


def _validate_startup_name_consistency() -> None:
    validate_sources_registry_consistency()
    expected_seed_by_module_path = {
        "scrapers.constructors.former_constructors_list": "constructors_former",
        "scrapers.constructors.indianapolis_only_constructors_list": (
            "constructors_indianapolis_only"
        ),
        "scrapers.drivers.female_drivers_list": "drivers_female",
        "scrapers.drivers.fatalities_list_scraper": "drivers_fatalities",
        "scrapers.engines.engine_manufacturers_list": "engines_manufacturers",
        "scrapers.engines.engine_regulation": "engines_regulations",
        "scrapers.engines.engine_restrictions": "engines_restrictions",
    }
    for module_path, seed_name in expected_seed_by_module_path.items():
        definition = MODULE_DEFINITIONS[module_path]
        if definition.output_json is None:
            continue
        configured_filename = Path(definition.output_json).name
        source = get_source_by_seed_name(seed_name, warn=False)
        canonical_filename = source.list_filename
        resolved_filename = resolve_list_filename(configured_filename, warn=False)
        if resolved_filename != canonical_filename:
            msg = (
                "Startup consistency check failed: "
                f"module {module_path!r} uses output filename {configured_filename!r}, "
                f"expected canonical {canonical_filename!r} (or a declared legacy alias)."
            )
            raise ValueError(msg)


_validate_startup_name_consistency()

_DOMAIN_SCRAPER_METADATA = get_domain_entrypoint_scraper_metadata()
DOMAIN_COMMANDS: dict[str, DomainCommand] = {}
for module_path in MODULE_DEFINITIONS:
    parts = module_path.split(".")
    if len(parts) < SCRAPER_MODULE_PATH_PARTS or parts[0] != "scrapers":
        continue
    if parts[-1] != "entrypoint":
        continue
    domain = parts[1]
    scraper_path = _DOMAIN_SCRAPER_METADATA.get(domain)
    if scraper_path is None:
        continue
    DOMAIN_COMMANDS[domain] = DomainCommand(
        name=domain,
        module_path=module_path,
        scraper_path=scraper_path,
    )


def _invoke_target(target: Callable[..., None], run_config: RunConfig) -> None:
    signature = inspect.signature(target)
    if "run_config" in signature.parameters:
        target(run_config=run_config)
        return
    target()


def _legacy_profile_choices() -> tuple[LegacyCliProfileName, ...]:
    return LEGACY_CLI_PROFILE_NAMES


def _build_profile_parser(
    default_profile: LegacyCliProfileName,
) -> argparse.ArgumentParser:
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


def _module_path_from_file(file_path: str) -> str:
    path = Path(file_path).resolve()
    suffixless_parts = path.with_suffix("").parts

    try:
        scrapers_index = suffixless_parts.index("scrapers")
    except ValueError as exc:
        msg = f"Cannot infer scrapers module path from {file_path!r}."
        raise ValueError(msg) from exc

    return ".".join(suffixless_parts[scrapers_index:])


def run_legacy_wrapper(module_path: str, argv: list[str] | None = None) -> None:
    spec = SCRAPER_REGISTRY[module_path]
    _, args = _parse_legacy_args(argv, spec.profile)
    run_config = build_run_config(base_config=spec.base_config, args=args)
    configure_logging(verbose=run_config.verbose, trace=run_config.trace)
    _invoke_target(spec.target, run_config)


def run_registered_module(module_path: str, argv: list[str] | None = None) -> None:
    """Run a legacy-compatible registered module command."""
    run_legacy_wrapper(module_path, argv)


def run_registered_module_for_caller(argv: list[str] | None = None) -> None:
    """Resolve caller module path and execute via command registry."""
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        msg = "Cannot infer caller module for legacy wrapper."
        raise RuntimeError(msg)

    try:
        caller_file = frame.f_back.f_code.co_filename
    finally:
        del frame

    run_registered_module(_module_path_from_file(caller_file), argv)


def _build_main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Canonical scraper CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("module", choices=tuple(sorted(MODULE_DEFINITIONS)))

    domain_parser = subparsers.add_parser("domain")
    domain_parser.add_argument("name", choices=tuple(sorted(DOMAIN_COMMANDS)))

    wiki_parser = subparsers.add_parser("wiki")
    wiki_parser.add_argument(
        "--mode",
        choices=("layer0", "layer1", "full"),
        default="layer0",
    )

    return parser


def _build_wiki_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Canonical wiki pipeline launcher")
    parser.add_argument(
        "--mode",
        choices=("layer0", "layer1", "full"),
        default="layer0",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        default=False,
    )
    return parser


def run_wiki_cli(argv: list[str] | None = None) -> None:
    parser = _build_wiki_parser()
    args = parser.parse_args(argv)
    configure_logging(verbose=args.verbose, trace=args.trace)

    app_module = importlib.import_module("layers.application")
    create_default_wiki_pipeline_application = (
        app_module.create_default_wiki_pipeline_application
    )
    app = create_default_wiki_pipeline_application(
        base_wiki_dir=DEFAULT_PATH_RESOLVER.exports_root.resolve(),
        base_debug_dir=DEFAULT_PATH_RESOLVER.debug_root.resolve(),
    )
    if args.mode in {"layer0", "full"}:
        app.run_layer_zero()
    if args.mode in {"layer1", "full"}:
        app.run_layer_one()
