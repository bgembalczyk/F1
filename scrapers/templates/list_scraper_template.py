"""Template for creating a new table-based list scraper module.

Usage (copy + rename + fill hooks):
1) copy this file to the target domain directory (e.g. ``scrapers/<domain>/...``),
2) rename classes/constants to the final domain names,
3) fill the schema/config hooks marked as TODO,
4) keep the ``SCRAPER_TEMPLATE_CONFIG`` contract unchanged for review consistency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper


@dataclass(frozen=True, slots=True)
class ListScraperTemplateConfig:
    """Uniform configuration contract for list scraper modules."""

    domain: str
    source_url: str
    section_id: str | None
    expected_headers: tuple[str, ...]


SCRAPER_TEMPLATE_CONFIG = ListScraperTemplateConfig(
    domain="TODO_domain",
    source_url="https://en.wikipedia.org/wiki/TODO_article",
    section_id="TODO_section_id",
    expected_headers=("TODO Header",),
)


class TODOListScraper(F1TableScraper):
    """TODO: replace with real list scraper docstring."""

    options_domain: ClassVar[str | None] = SCRAPER_TEMPLATE_CONFIG.domain
    options_profile: ClassVar[str | None] = "list_scraper"

    schema_columns = [
        # TODO: replace with real schema columns.
        column("TODO Header", "todo_field"),
    ]

    CONFIG: ClassVar[ScraperConfig] = build_scraper_config(
        url=SCRAPER_TEMPLATE_CONFIG.source_url,
        section_id=SCRAPER_TEMPLATE_CONFIG.section_id,
        expected_headers=list(SCRAPER_TEMPLATE_CONFIG.expected_headers),
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=RECORD_FACTORIES.mapping(),
    )


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
