from __future__ import annotations

from typing import Protocol

from scrapers.base.factory.legacy_adapter import LegacyScraperAdapter
from scrapers.base.factory.option_adapter import OptionsScraperAdapter
from scrapers.base.factory.run_config_options_mapper import RunConfigOptionsMapper


class ScraperCreationAdapter(Protocol):
    def supports(self, ctor: object) -> bool: ...

    def create(self, *, context: object, ctor: object) -> object: ...


class ScraperAdapterChainProvider(Protocol):
    def build(self, *, mapper: RunConfigOptionsMapper) -> tuple[ScraperCreationAdapter, ...]: ...


class DefaultScraperAdapterChainProvider:
    def build(
        self,
        *,
        mapper: RunConfigOptionsMapper,
    ) -> tuple[ScraperCreationAdapter, ...]:
        return (
            OptionsScraperAdapter(mapper),
            LegacyScraperAdapter(),
        )
