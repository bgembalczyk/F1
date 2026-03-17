import inspect
from dataclasses import dataclass

from scrapers.base.abc import ABCScraper
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig


@dataclass(frozen=True)
class RunConfigOptionsMapper:
    """Jawne mapowanie RunConfig -> ScraperOptions."""

    def apply(
        self,
        *,
        run_config: RunConfig,
        options: ScraperOptions,
        run_id: str,
    ) -> None:
        if run_config.debug_dir is not None:
            options.debug_dir = run_config.debug_dir
        if run_config.cache_dir is not None:
            options.cache_dir = run_config.cache_dir
        if run_config.cache_ttl is not None:
            options.cache_ttl = run_config.cache_ttl
        if run_config.cache_adapter is not None:
            options.cache_adapter = run_config.cache_adapter
        if run_config.http_timeout is not None:
            options.http_timeout = run_config.http_timeout
        if run_config.http_retries is not None:
            options.http_retries = run_config.http_retries
        if run_config.http_backoff_seconds is not None:
            options.http_backoff_seconds = run_config.http_backoff_seconds

        options.run_id = run_id
        options.quality_report = run_config.quality_report
        options.error_report = run_config.error_report


@dataclass(frozen=True)
class ScraperCreationContext:
    scraper_cls: type[ABCScraper]
    run_config: RunConfig
    run_id: str
    supports_urls: bool


class _ConstructorIntrospection:
    def __init__(self, scraper_cls: type[ABCScraper]) -> None:
        self._signature = inspect.signature(scraper_cls.__init__)
        self._parameters = self._signature.parameters

    def accepts(self, param_name: str) -> bool:
        if param_name in self._parameters:
            return True
        return any(
            param.kind == inspect.Parameter.VAR_KEYWORD
            for param in self._parameters.values()
        )


class _OptionsScraperAdapter:
    def __init__(self, mapper: RunConfigOptionsMapper) -> None:
        self._mapper = mapper

    def supports(self, ctor: _ConstructorIntrospection) -> bool:
        return ctor.accepts("options")

    def create(
        self,
        *,
        context: ScraperCreationContext,
        ctor: _ConstructorIntrospection,
    ) -> ABCScraper:
        kwargs = dict(context.run_config.scraper_kwargs)
        options = context.run_config.options or ScraperOptions()
        self._mapper.apply(
            run_config=context.run_config,
            options=options,
            run_id=context.run_id,
        )

        if context.supports_urls:
            options.include_urls = context.run_config.include_urls

        kwargs.setdefault("options", options)
        if ctor.accepts("run_id"):
            kwargs.setdefault("run_id", context.run_id)
        return context.scraper_cls(**kwargs)


class _LegacyScraperAdapter:
    def supports(self, _ctor: _ConstructorIntrospection) -> bool:
        return True

    def create(
        self,
        *,
        context: ScraperCreationContext,
        ctor: _ConstructorIntrospection,
    ) -> ABCScraper:
        kwargs = dict(context.run_config.scraper_kwargs)
        if ctor.accepts("run_id"):
            kwargs.setdefault("run_id", context.run_id)
        if context.supports_urls and ctor.accepts("include_urls"):
            kwargs.setdefault("include_urls", context.run_config.include_urls)
        return context.scraper_cls(**kwargs)


class ScraperFactory:
    def __init__(self, *, mapper: RunConfigOptionsMapper | None = None) -> None:
        resolved_mapper = mapper or RunConfigOptionsMapper()
        self._adapters = (
            _OptionsScraperAdapter(resolved_mapper),
            _LegacyScraperAdapter(),
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
        ctor = _ConstructorIntrospection(scraper_cls)
        for adapter in self._adapters:
            if adapter.supports(ctor):
                return adapter.create(context=context, ctor=ctor)
        msg = f"No adapter available for {scraper_cls.__name__}"
        raise TypeError(msg)
