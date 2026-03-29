from collections.abc import Sequence

from scrapers.base.abc import ABCScraper
from scrapers.base.factory.constructor_introspection import ConstructorIntrospection
from scrapers.base.factory.creation_adapter_protocol import (
    ScraperCreationAdapterProtocol,
)
from scrapers.base.factory.creation_context import ScraperCreationContext
from scrapers.base.factory.legacy_adapter import LegacyScraperAdapter
from scrapers.base.factory.option_adapter import OptionsScraperAdapter
from scrapers.base.factory.run_config_options_mapper import RunConfigOptionsMapper
from scrapers.base.run_config import RunConfig


class ScraperFactory:
    def __init__(
        self,
        *,
        mapper: RunConfigOptionsMapper | None = None,
        adapters: Sequence[ScraperCreationAdapterProtocol] | None = None,
    ) -> None:
        resolved_mapper = mapper or RunConfigOptionsMapper()
        self._adapters = tuple(adapters or self.default_adapters(mapper=resolved_mapper))

    @staticmethod
    def default_adapters(
        *,
        mapper: RunConfigOptionsMapper | None = None,
    ) -> list[ScraperCreationAdapterProtocol]:
        resolved_mapper = mapper or RunConfigOptionsMapper()
        return [
            OptionsScraperAdapter(resolved_mapper),
            LegacyScraperAdapter(),
        ]

    def create(
        self,
        *,
        scraper_cls: type[ABCScraper],
        run_config: RunConfig,
        run_id: str,
        supports_urls: bool = True,
    ) -> ABCScraper:
        context = ScraperCreationContext(
            scraper_cls=scraper_cls,
            run_config=run_config,
            run_id=run_id,
            supports_urls=supports_urls,
        )
        ctor = ConstructorIntrospection(scraper_cls)
        for adapter in self._adapters:
            if adapter.supports(ctor):
                return adapter.create(context=context, ctor=ctor)
        msg = f"No adapter available for {scraper_cls.__name__}"
        raise TypeError(msg)
