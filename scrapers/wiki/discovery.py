from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from scrapers.wiki.contants import COMPONENT_METADATA_ATTR

if TYPE_CHECKING:
    from types import ModuleType


@dataclass(frozen=True)
class ComponentMetadata:
    domain: str
    seed_name: str
    layer: str
    output_category: str
    component_type: str
    default_output_path: str | None = None
    legacy_output_path: str | None = None


@dataclass(frozen=True)
class DiscoveredComponent:
    cls: type[Any]
    metadata: ComponentMetadata


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _path_to_module(path: Path) -> str:
    rel = path.relative_to(_repo_root()).with_suffix("")
    return ".".join(rel.parts)


def _iter_discovery_module_names() -> tuple[str, ...]:
    root = _repo_root()
    module_paths: set[Path] = set()
    module_paths.update(root.glob("scrapers/*/entrypoint.py"))
    module_paths.update(root.glob("scrapers/*/list/*.py"))
    module_paths.add(root / "scrapers/wiki/orchestration.py")

    return tuple(
        sorted(_path_to_module(path) for path in module_paths if path.is_file()),
    )


def _read_component_metadata(candidate: type[Any]) -> ComponentMetadata | None:
    raw = getattr(candidate, COMPONENT_METADATA_ATTR, None)
    if raw is None:
        return None
    if isinstance(raw, ComponentMetadata):
        return raw
    if isinstance(raw, dict):
        return ComponentMetadata(**raw)
    message = f"Unsupported metadata format for {candidate!r}: {type(raw)!r}"
    raise TypeError(message)


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


def build_layer_one_runner_map_discovered() -> dict[str, Any]:
    runner_map: dict[str, Any] = {}
    source_cls_by_seed: dict[str, type[Any]] = {}
    for component in discover_components():
        metadata = component.metadata
        if metadata.layer != "layer_one" or metadata.component_type != "runner":
            continue
        existing_cls = source_cls_by_seed.get(metadata.seed_name)
        if existing_cls is not None and existing_cls is not component.cls:
            msg = f"Duplicate runner seed_name discovered: {metadata.seed_name}"
            raise ValueError(msg)
        source_cls_by_seed[metadata.seed_name] = component.cls
        runner_map[metadata.seed_name] = component.cls()
    return runner_map


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


def validate_discovery_metadata_completeness() -> None:
    module_names = _iter_discovery_module_names()
    missing: list[str] = []

    for module_name in module_names:
        module = importlib.import_module(module_name)
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if candidate.__module__ != module.__name__:
                continue
            if (
                candidate.__name__.endswith("Runner")
                and candidate.__name__ != "LayerJobRunner"
            ):
                if getattr(candidate, COMPONENT_METADATA_ATTR, None) is None:
                    missing.append(f"{module_name}.{candidate.__name__}")

        list_scraper_cls = getattr(module, "LIST_SCRAPER_CLASS", None)
        if (
            inspect.isclass(list_scraper_cls)
            and getattr(list_scraper_cls, COMPONENT_METADATA_ATTR, None) is None
        ):
            missing.append(f"{list_scraper_cls.__module__}.{list_scraper_cls.__name__}")

    if missing:
        msg = "Discovery metadata missing for components: " + ", ".join(sorted(missing))
        raise ValueError(msg)
