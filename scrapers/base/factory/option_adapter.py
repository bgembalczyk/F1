from scrapers.base.abc import ABCScraper
from scrapers.base.factory.constructor_introspection import ConstructorIntrospection
from scrapers.base.factory.creation_context import ScraperCreationContext
from scrapers.base.factory.run_config_options_mapper import RunConfigOptionsMapper
from scrapers.base.options import ScraperOptions


class OptionsScraperAdapter:
    def __init__(self, mapper: RunConfigOptionsMapper) -> None:
        self._mapper = mapper

    def supports(self, ctor: ConstructorIntrospection) -> bool:
        return ctor.accepts("options")

    def create(
        self,
        *,
        context: ScraperCreationContext,
        ctor: ConstructorIntrospection,
    ) -> ABCScraper:
        kwargs = self._build_kwargs(context)
        options = self._resolve_options(context)
        self._mapper.apply(
            run_config=context.run_config,
            options=options,
            run_id=context.run_id,
        )
        if context.supports_urls:
            options.include_urls = context.run_config.include_urls
        if ctor.accepts_explicitly("run_id"):
            kwargs.setdefault("run_id", context.run_id)
        kwargs.setdefault("options", options)
        return context.scraper_cls(**kwargs)

    @staticmethod
    def _build_kwargs(context: ScraperCreationContext) -> dict[str, object]:
        return dict(context.run_config.scraper_kwargs)

    @staticmethod
    def _resolve_options(context: ScraperCreationContext) -> ScraperOptions:
        return context.run_config.options or ScraperOptions()
