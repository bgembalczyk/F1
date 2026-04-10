from __future__ import annotations

from scrapers.configs.public import RuntimeConfig
from scrapers.configs.public import TableConfig

CONFIG_IMPORT_MIGRATIONS: dict[str, str] = {
    "scrapers.config.ScraperConfig": "scrapers.config.RuntimeConfig",
    "scrapers.config_table.ScraperConfig": "scrapers.config_table.TableConfig",
}

__all__ = [
    "RuntimeConfig",
    "TableConfig",
    "CONFIG_IMPORT_MIGRATIONS",
]
