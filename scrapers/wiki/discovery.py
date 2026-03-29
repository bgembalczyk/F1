from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from layers.orchestration.runners.layer_job import LayerJobRunner
from layers.orchestration.runners.metadata import RunnerMetadata
from scrapers.wiki.component_metadata import ComponentMetadata
from scrapers.wiki.component_metadata import parse_component_metadata
from scrapers.wiki.component_metadata import RUNNER_KIND
from scrapers.wiki.constants import COMPONENT_METADATA_ATTR

if TYPE_CHECKING:
    from types import ModuleType


@dataclass(frozen=True)
class DiscoveredComponent:
    cls: type[Any]
    metadata: ComponentMetadata


@dataclass(frozen=True)
class DiscoveredRunner:
    cls: type[LayerJobRunner]
    metadata: RunnerMetadata


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _path_to_module(path: Path) -> str:
    rel = path.relative_to(_repo_root()).with_suffix("")
    return ".".join(rel.parts)


def _iter_discovery_module_paths(root: Path) -> set[Path]:
    module_paths: set[Path] = set()
    module_paths.update(root.glob("scrapers/*/entrypoint.py"))
    module_paths.update(root.glob("scrapers/*/list/*.py"))
    module_paths.add(root / "scrapers/wiki/orchestration/helpers.py")
    return module_paths


def _iter_discovery_module_names() -> tuple[str, ...]:
    root = _repo_root()
    module_paths = _iter_discovery_module_paths(root)
    return tuple(
        sorted(_path_to_module(path) for path in module_paths if path.is_file()),
    )


def _read_component_metadata(candidate: type[Any]) -> ComponentMetadata | None:
    raw = getattr(candidate, COMPONENT_METADATA_ATTR, None)
    if raw is None:
        return None
    metadata = parse_component_metadata(raw)
    setattr(candidate, COMPONENT_METADATA_ATTR, metadata)
    return metadata


def discover_components() -> tuple[DiscoveredComponent, ...]:
    discovered: list[DiscoveredComponent] = []
    for module_name in _iter_discovery_module_names():
        module = importlib.import_module(module_name)
        discovered.extend(_discover_components_in_module(module))
    return tuple(discovered)


def _discover_components_in_module(module: ModuleType) -> list[DiscoveredComponent]:
    result: list[DiscoveredComponent] = []
    seen: set[type[Any]] = set()

    for _, candidate in inspect.getmembers(module, inspect.isclass):
        metadata = _read_component_metadata(candidate)
        if metadata is None:
            continue
        result.append(DiscoveredComponent(cls=candidate, metadata=metadata))
        seen.add(candidate)

    list_scraper_cls = getattr(module, "LIST_SCRAPER_CLASS", None)
    if inspect.isclass(list_scraper_cls) and list_scraper_cls not in seen:
        metadata = _read_component_metadata(list_scraper_cls)
        if metadata is not None:
            result.append(DiscoveredComponent(cls=list_scraper_cls, metadata=metadata))

    return result


def discover_layer_one_runners() -> dict[str, DiscoveredRunner]:
    runner_components: dict[str, DiscoveredRunner] = {}
    for component in discover_components():
        metadata = component.metadata
        if metadata.layer != "layer_one" or metadata.component_type != RUNNER_KIND:
            continue
        if not issubclass(component.cls, LayerJobRunner):
            msg = f"Discovered runner {component.cls.__name__} must inherit LayerJobRunner"
            raise TypeError(msg)
        runner_metadata = RunnerMetadata.from_component_metadata(metadata)
        existing = runner_components.get(runner_metadata.seed_name)
        if existing is not None and existing.cls is not component.cls:
            msg = f"Duplicate runner seed_name discovered: {runner_metadata.seed_name}"
            raise ValueError(msg)
        runner_components[runner_metadata.seed_name] = DiscoveredRunner(
            cls=component.cls,
            metadata=runner_metadata,
        )
    return runner_components


def build_layer_one_runner_map_discovered() -> dict[str, LayerJobRunner]:
    return {
        seed_name: component.cls()
        for seed_name, component in discover_layer_one_runners().items()
    }


def discover_layer_one_seed_components() -> dict[str, DiscoveredComponent]:
    seed_components: dict[str, DiscoveredComponent] = {}
    for component in discover_components():
        metadata = component.metadata
        if metadata.layer != "layer_one" or metadata.component_type != "list_scraper":
            continue
        existing = seed_components.get(metadata.seed_name)
        if existing is not None and existing.cls is not component.cls:
            msg = f"Duplicate seed_name discovered: {metadata.seed_name}"
            raise ValueError(msg)
        seed_components[metadata.seed_name] = component
    return seed_components
