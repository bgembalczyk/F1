"""Backward-compatible re-export for module naming aliases.

Canonical compatibility definitions live in ``scrapers.legacy.module_naming_compat``.
"""

from scrapers.legacy.module_naming_compat import MODULE_NAMING_ALIASES
from scrapers.legacy.module_naming_compat import ModuleNamingAlias
from scrapers.legacy.module_naming_compat import module_naming_alias_map

__all__ = ["MODULE_NAMING_ALIASES", "ModuleNamingAlias", "module_naming_alias_map"]
