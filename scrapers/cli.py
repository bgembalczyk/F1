"""Compatibility shim for legacy ``scrapers.cli`` imports.

The canonical command metadata now lives in domain entrypoint abstractions.
"""

from __future__ import annotations

from dataclasses import dataclass

from scrapers.base.domain_entrypoint import get_domain_entrypoint_scraper_metadata


@dataclass(frozen=True)
class ModuleDefinition:
    """Legacy-compatible module definition metadata."""

    module_path: str


MODULE_DEFINITIONS: dict[str, ModuleDefinition] = {
    domain: ModuleDefinition(module_path=module_path)
    for domain, module_path in get_domain_entrypoint_scraper_metadata().items()
}

__all__ = ["MODULE_DEFINITIONS", "ModuleDefinition"]
