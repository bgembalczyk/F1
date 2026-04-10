from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

from scrapers.adapters.legacy import LegacyScraperAdapter
from scrapers.adapters.option import OptionsScraperAdapter
from scrapers.run_config_options_mapper import RunConfigOptionsMapper


class ScraperCreationAdapter(Protocol):
    def supports(self, ctor: object) -> bool: ...

    def create(self, *, context: object, ctor: object) -> object: ...


def default_scraper_creation_adapters(
    *,
    mapper: RunConfigOptionsMapper,
) -> tuple[ScraperCreationAdapter, ...]:
    return (
        # di-antipattern-allow: intentional composition point.
        OptionsScraperAdapter(mapper),
        # di-antipattern-allow: intentional composition point.
        LegacyScraperAdapter(),
    )
