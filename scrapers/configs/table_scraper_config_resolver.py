"""Helpers for resolving table scraper configuration."""

from __future__ import annotations

from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.config import ScraperConfig as TableScraperConfig


def resolve_table_scraper_config(
    scraper: object,
    explicit_config: TableScraperConfig | None,
) -> TableScraperConfig:
    """Resolve table scraper configuration from explicit config, class CONFIG, or attrs."""
    if explicit_config is not None:
        return explicit_config

    class_config = getattr(scraper, "CONFIG", None)
    if class_config is not None:
        return class_config

    url = getattr(scraper, "url", None)
    if not isinstance(url, str) or not url.strip():
        msg = "ScraperConfig must be provided for table scrapers."
        raise ValueError(msg)

    return TableScraperConfig(
        url=url,
        section_id=getattr(scraper, "section_id", None),
        expected_headers=getattr(scraper, "expected_headers", None),
        column_map=getattr(scraper, "column_map", {}),
        columns=getattr(scraper, "columns", {}),
        table_css_class=getattr(scraper, "table_css_class", "wikitable"),
        record_factory=getattr(scraper, "record_factory", None),
        model_class=getattr(scraper, "model_class", None),
        default_column=getattr(scraper, "default_column", AutoColumn()),
    )
