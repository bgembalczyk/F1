from scrapers.base.abc import ABCScraper
from scrapers.base.factory.adapter_chain import ScraperCreationAdapter
from scrapers.base.factory.adapter_chain import default_scraper_creation_adapters
from scrapers.base.factory.constructor_introspection import ConstructorIntrospection
from scrapers.base.factory.creation_context import ScraperCreationContext
from scrapers.base.factory.run_config_options_mapper import RunConfigOptionsMapper
from scrapers.base.run_config import RunConfig


class ScraperFactory:
    def __init__(
        self,
        *,
        mapper: RunConfigOptionsMapper | None = None,
        adapters: tuple[ScraperCreationAdapter, ...] | None = None,
    ) -> None:
        resolved_mapper = mapper or RunConfigOptionsMapper()
        self._adapters = adapters or default_scraper_creation_adapters(
            mapper=resolved_mapper,
        )

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
                return self._create_with_adapter(adapter, context=context, ctor=ctor)
        msg = f"No adapter available for {scraper_cls.__name__}"
        raise TypeError(msg)

    @staticmethod
    def _create_with_adapter(
        adapter: ScraperCreationAdapter,
        *,
        context: ScraperCreationContext,
        ctor: ConstructorIntrospection,
    ) -> ABCScraper:
        """Invoke adapter.create with compatibility for older adapter signatures."""

        try:
            return adapter.create(context=context, ctor=ctor)
        except TypeError:
            pass

        try:
            return adapter.create(context=context, _ctor=ctor)
        except TypeError:
            pass

        try:
            return adapter.create(context=context)
        except TypeError:
            return adapter.create(context, ctor)
