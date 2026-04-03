from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from scrapers.wiki.component_metadata import LIST_SCRAPER_KIND
from scrapers.wiki.component_metadata import RUNNER_KIND
from scrapers.wiki.component_metadata import ComponentMetadata
from scrapers.wiki.component_metadata import parse_component_metadata
from scrapers.wiki.constants import COMPONENT_METADATA_ATTR
from scrapers.wiki.protocols import DiscoveredListScraperClassProtocol
from scrapers.wiki.protocols import DiscoveredRunnerClassProtocol
from scrapers.wiki.protocols import DiscoveredRunnerProtocol

DiscoveredComponentClass = (
    DiscoveredRunnerClassProtocol | DiscoveredListScraperClassProtocol
)

if TYPE_CHECKING:
    from types import ModuleType


@dataclass(frozen=True)
class DiscoveredComponent:
    cls: DiscoveredComponentClass
    metadata: ComponentMetadata


_COMPONENT_METADATA_CACHE: dict[tuple[str, str], ComponentMetadata | None] = {}


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
    cache_key = (candidate.__module__, candidate.__qualname__)
    cached = _COMPONENT_METADATA_CACHE.get(cache_key)
    if cached is not None:
        return cached

    if cache_key in _COMPONENT_METADATA_CACHE:
        return None

    raw = getattr(candidate, COMPONENT_METADATA_ATTR, None)
    if raw is None:
        _COMPONENT_METADATA_CACHE[cache_key] = None
        return None
    metadata = parse_component_metadata(raw)
    _COMPONENT_METADATA_CACHE[cache_key] = metadata
    return metadata


def _clear_component_metadata_cache() -> None:
    _COMPONENT_METADATA_CACHE.clear()


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
        result.append(
            DiscoveredComponent(
                cls=_coerce_discovered_component_class(candidate, metadata=metadata),
                metadata=metadata,
            ),
        )
        seen.add(candidate)

    list_scraper_cls = getattr(module, "LIST_SCRAPER_CLASS", None)
    if inspect.isclass(list_scraper_cls) and list_scraper_cls not in seen:
        metadata = _read_component_metadata(list_scraper_cls)
        if metadata is not None:
            result.append(
                DiscoveredComponent(
                    cls=_coerce_discovered_component_class(
                        list_scraper_cls,
                        metadata=metadata,
                    ),
                    metadata=metadata,
                ),
            )

    return result


def _coerce_discovered_component_class(
    candidate: Any,
    *,
    metadata: ComponentMetadata,
) -> DiscoveredComponentClass:
    if metadata.component_type == RUNNER_KIND:
        if not callable(candidate):
            msg = f"Runner component '{candidate}' must be callable"
            raise TypeError(msg)
        return cast("DiscoveredRunnerClassProtocol", candidate)
    if metadata.component_type == LIST_SCRAPER_KIND:
        config = getattr(candidate, "CONFIG", None)
        url = getattr(config, "url", None)
        if not isinstance(url, str) or not url.strip():
            msg = f"List scraper component '{candidate}' must expose CONFIG.url"
            raise TypeError(msg)
        return cast("DiscoveredListScraperClassProtocol", candidate)
    return cast("DiscoveredComponentClass", candidate)


def build_layer_one_runner_map_discovered() -> dict[str, DiscoveredRunnerProtocol]:
    runner_map: dict[str, DiscoveredRunnerProtocol] = {}
    source_cls_by_seed: dict[str, type[Any]] = {}
    for component in discover_components():
        metadata = component.metadata
        if metadata.layer != "layer_one" or metadata.component_type != RUNNER_KIND:
            continue
        existing_cls = source_cls_by_seed.get(metadata.seed_name)
        if existing_cls is not None and existing_cls is not component.cls:
            msg = f"Duplicate runner seed_name discovered: {metadata.seed_name}"
            raise ValueError(msg)
        source_cls_by_seed[metadata.seed_name] = component.cls
        runner = component.cls()
        if not hasattr(runner, "run") or not callable(runner.run):
            msg = f"Runner '{metadata.seed_name}' does not implement run() contract"
            raise TypeError(msg)
        runner_map[metadata.seed_name] = cast("DiscoveredRunnerProtocol", runner)
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
