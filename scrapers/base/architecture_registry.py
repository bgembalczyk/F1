from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile

if TYPE_CHECKING:
    from collections.abc import Callable

    from scrapers.base.run_config import RunConfig


@dataclass(frozen=True)
class DomainEntrypointRegistryEntry:
    scraper_path: str
    default_output_json: str | Path
    run_config_profile_name: str
    default_output_csv: str | Path | None = None


@dataclass(frozen=True)
class LayerOneRunnerRegistryEntry:
    seed_name: str
    runner_kind: str
    component_metadata: dict[str, str]
    export_function_path: str | None = None


@dataclass(frozen=True)
class ArchitectureRegistry:
    domains: tuple[str, ...]
    entrypoint_domains: tuple[str, ...]
    layers: tuple[str, ...]
    required_layers_by_domain: dict[str, tuple[str, ...]]
    domain_entrypoints: dict[str, DomainEntrypointRegistryEntry]
    layer_one_runners: tuple[LayerOneRunnerRegistryEntry, ...]


def _strict_quality_profile() -> RunConfig:
    return build_run_profile(RunProfileName.STRICT)


def _minimal_profile() -> RunConfig:
    return build_run_profile(RunProfileName.MINIMAL)


def _minimal_debug_profile() -> RunConfig:
    return build_run_profile(RunProfileName.DEBUG)


RUN_PROFILE_FACTORIES: dict[str, Callable[[], RunConfig]] = {
    "strict_quality_profile": _strict_quality_profile,
    "minimal_profile": _minimal_profile,
    "minimal_debug_profile": _minimal_debug_profile,
}

ARCHITECTURE_REGISTRY = ArchitectureRegistry(
    domains=(
        "drivers",
        "constructors",
        "circuits",
        "seasons",
        "grands_prix",
        "engines",
        "points",
        "sponsorship_liveries",
        "tyres",
    ),
    entrypoint_domains=(
        "drivers",
        "constructors",
        "circuits",
        "seasons",
        "grands_prix",
    ),
    layers=("list", "sections", "infobox", "postprocess"),
    required_layers_by_domain={
        "drivers": ("list", "sections", "infobox", "postprocess"),
        "constructors": ("list", "sections", "infobox", "postprocess"),
        "circuits": ("list", "sections", "infobox", "postprocess"),
        "seasons": ("list", "sections", "postprocess"),
        "grands_prix": ("list", "sections"),
    },
    domain_entrypoints={
        "drivers": DomainEntrypointRegistryEntry(
            scraper_path="scrapers.drivers.list_scraper:F1DriversListScraper",
            default_output_json="drivers/f1_drivers.json",
            run_config_profile_name="strict_quality_profile",
        ),
        "seasons": DomainEntrypointRegistryEntry(
            scraper_path="scrapers.seasons.list_scraper:SeasonsListScraper",
            default_output_json="seasons/f1_seasons.json",
            default_output_csv="seasons/f1_seasons.csv",
            run_config_profile_name="minimal_profile",
        ),
        "grands_prix": DomainEntrypointRegistryEntry(
            scraper_path="scrapers.grands_prix.list_scraper:GrandsPrixListScraper",
            default_output_json="grands_prix/f1_grands_prix_by_title.json",
            default_output_csv="grands_prix/f1_grands_prix_by_title.csv",
            run_config_profile_name="minimal_profile",
        ),
        "circuits": DomainEntrypointRegistryEntry(
            scraper_path="scrapers.circuits.list_scraper:CircuitsListScraper",
            default_output_json="circuits/f1_circuits.json",
            default_output_csv="circuits/f1_circuits.csv",
            run_config_profile_name="strict_quality_profile",
        ),
        "constructors": DomainEntrypointRegistryEntry(
            scraper_path=(
                "scrapers.constructors.current_constructors_list:"
                "CurrentConstructorsListScraper"
            ),
            default_output_json="constructors/f1_constructors_{year}.json",
            default_output_csv="constructors/f1_constructors_{year}.csv",
            run_config_profile_name="minimal_debug_profile",
        ),
    },
    layer_one_runners=(
        LayerOneRunnerRegistryEntry(
            seed_name="grands_prix",
            runner_kind="grand_prix",
            component_metadata={
                "domain": "grands_prix",
                "seed_name": "grands_prix",
                "layer": "layer_one",
                "output_category": "grands_prix",
                "component_type": "runner",
            },
        ),
        LayerOneRunnerRegistryEntry(
            seed_name="circuits",
            runner_kind="function_export",
            export_function_path=(
                "scrapers.circuits.helpers.export:export_complete_circuits"
            ),
            component_metadata={
                "domain": "circuits",
                "seed_name": "circuits",
                "layer": "layer_one",
                "output_category": "circuits",
                "component_type": "runner",
            },
        ),
        LayerOneRunnerRegistryEntry(
            seed_name="drivers",
            runner_kind="function_export",
            export_function_path="scrapers.drivers.helpers.export:export_complete_drivers",
            component_metadata={
                "domain": "drivers",
                "seed_name": "drivers",
                "layer": "layer_one",
                "output_category": "drivers",
                "component_type": "runner",
            },
        ),
        LayerOneRunnerRegistryEntry(
            seed_name="seasons",
            runner_kind="function_export",
            export_function_path="scrapers.seasons.helpers:export_complete_seasons",
            component_metadata={
                "domain": "seasons",
                "seed_name": "seasons",
                "layer": "layer_one",
                "output_category": "seasons",
                "component_type": "runner",
            },
        ),
        LayerOneRunnerRegistryEntry(
            seed_name="constructors",
            runner_kind="function_export",
            export_function_path=(
                "scrapers.constructors.helpers.export:export_complete_constructors"
            ),
            component_metadata={
                "domain": "constructors",
                "seed_name": "constructors",
                "layer": "layer_one",
                "output_category": "constructors",
                "component_type": "runner",
            },
        ),
    ),
)


def get_run_profile_factory(profile_name: str) -> Callable[[], RunConfig]:
    return RUN_PROFILE_FACTORIES[profile_name]


def _split_import_path(path: str) -> tuple[str, str]:
    module_name, attr_name = path.split(":", maxsplit=1)
    return module_name, attr_name


def _validate_domain_directories(
    root: Path,
    registry: ArchitectureRegistry,
) -> list[str]:
    scrapers_root = root / "scrapers"
    errors = [
        f"Missing domain directory: scrapers/{domain}"
        for domain in registry.domains
        if not (scrapers_root / domain).is_dir()
    ]
    errors.extend(
        [
            f"Missing entrypoint for registry domain: scrapers/{domain}/entrypoint.py"
            for domain in registry.entrypoint_domains
            if not (scrapers_root / domain / "entrypoint.py").is_file()
        ],
    )
    return errors


def _validate_import_target(path: str) -> str | None:
    module_name, attr_name = _split_import_path(path)
    try:
        module = import_module(module_name)
    except (AttributeError, ImportError, ModuleNotFoundError, ValueError) as exc:
        return f"Cannot import module '{module_name}' ({exc})"
    if not hasattr(module, attr_name):
        return f"Missing attribute '{attr_name}' in module '{module_name}'"
    return None


def _validate_entrypoint_scrapers(registry: ArchitectureRegistry) -> list[str]:
    errors: list[str] = []
    for domain, entry in registry.domain_entrypoints.items():
        target_error = _validate_import_target(entry.scraper_path)
        if target_error is not None:
            errors.append(f"Domain '{domain}': {target_error}")
    return errors


def _validate_layer_one_runners(registry: ArchitectureRegistry) -> list[str]:
    errors: list[str] = []
    for runner in registry.layer_one_runners:
        if runner.component_metadata.get("seed_name") != runner.seed_name:
            errors.append(f"Runner seed mismatch for '{runner.seed_name}'")
        if runner.runner_kind != "function_export":
            continue
        if runner.export_function_path is None:
            errors.append(f"Runner '{runner.seed_name}' missing export_function_path")
            continue
        target_error = _validate_import_target(runner.export_function_path)
        if target_error is not None:
            errors.append(f"Runner '{runner.seed_name}': {target_error}")
    return errors


def validate_architecture_registry_consistency(
    *,
    repo_root: Path | None = None,
    registry: ArchitectureRegistry = ARCHITECTURE_REGISTRY,
) -> tuple[str, ...]:
    root = repo_root or Path(__file__).resolve().parents[2]
    errors: list[str] = []
    errors.extend(_validate_domain_directories(root, registry))
    errors.extend(_validate_entrypoint_scrapers(registry))
    errors.extend(_validate_layer_one_runners(registry))
    return tuple(errors)
