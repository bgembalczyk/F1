from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

from scrapers.base.factory.legacy_adapter import LegacyScraperAdapter
from scrapers.base.factory.option_adapter import OptionsScraperAdapter

if TYPE_CHECKING:
    from scrapers.base.factory.run_config_options_mapper import RunConfigOptionsMapper


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
