from scrapers.base.abc import ABCScraper
from scrapers.base.factory.constructor_introspection import ConstructorIntrospection
from scrapers.base.factory.creation_context import ScraperCreationContext


class LegacyScraperAdapter:
    def supports(self, _ctor: ConstructorIntrospection) -> bool:
        return True

    def create(
        self,
        *,
        context: ScraperCreationContext,
        ctor: ConstructorIntrospection,
    ) -> ABCScraper:
        kwargs = dict(context.run_config.scraper_kwargs)
        if ctor.accepts("run_id"):
            kwargs["run_id"] = context.run_id
        if context.supports_urls and ctor.accepts("include_urls"):
            kwargs.setdefault("include_urls", context.run_config.include_urls)
        return context.scraper_cls(**kwargs)
