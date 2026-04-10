from __future__ import annotations

from scrapers.config import RuntimeScraperConfig
from scrapers.config import RuntimeScraperConfig as LegacyRuntimeScraperConfig
from scrapers.config_table import TableScraperConfig
from scrapers.config_table import TableScraperConfig as LegacyTableScraperConfig

CONFIG_IMPORT_MIGRATIONS: dict[str, str] = {
    "scrapers.config.ScraperConfig": "scrapers.config.RuntimeScraperConfig",
    "scrapers.config_table.ScraperConfig": "scrapers.config_table.TableScraperConfig",
}

__all__ = [
    "RuntimeScraperConfig",
    "TableScraperConfig",
    "LegacyRuntimeScraperConfig",
    "LegacyTableScraperConfig",
    "CONFIG_IMPORT_MIGRATIONS",
]
