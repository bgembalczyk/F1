"""Compatibility shim exposing CLI module registry metadata for tests/docs."""

from __future__ import annotations

from dataclasses import dataclass

from scrapers.base.domain_entrypoint import get_domain_entrypoint_scraper_metadata


@dataclass(frozen=True)
class ModuleDefinition:
    module_path: str
    target_path: str


MODULE_DEFINITIONS: dict[str, ModuleDefinition] = {
    module_path: ModuleDefinition(
        module_path=module_path,
        target_path=scraper_path,
    )
    for module_path, scraper_path in get_domain_entrypoint_scraper_metadata().items()
}

