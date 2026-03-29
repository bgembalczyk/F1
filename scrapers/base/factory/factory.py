from scrapers.base.abc import ABCScraper
from scrapers.base.factory.adapter_chain import DefaultScraperAdapterChainProvider
from scrapers.base.factory.adapter_chain import ScraperAdapterChainProvider
from scrapers.base.factory.constructor_introspection import ConstructorIntrospection
from scrapers.base.factory.creation_context import ScraperCreationContext
from scrapers.base.factory.run_config_options_mapper import RunConfigOptionsMapper
from scrapers.base.run_config import RunConfig


class ScraperFactory:
    def __init__(
        self,
        *,
        mapper: RunConfigOptionsMapper | None = None,
        adapter_chain_provider: ScraperAdapterChainProvider | None = None,
    ) -> None:
        resolved_mapper = mapper or RunConfigOptionsMapper()
        chain_provider = adapter_chain_provider or DefaultScraperAdapterChainProvider()
        self._adapters = chain_provider.build(mapper=resolved_mapper)

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
