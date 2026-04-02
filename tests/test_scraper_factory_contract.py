# ruff: noqa: PLR2004
from scrapers.base.factory.factory import ScraperFactory
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig


class NewStyleScraper:
    def __init__(self, *, options: ScraperOptions, run_id: str | None = None) -> None:
        self.options = options
        self.run_id = run_id

    def fetch(self):
        return []


class LegacyScraper:
    def __init__(self, *, include_urls: bool, run_id: str | None = None) -> None:
        self.include_urls = include_urls
        self.run_id = run_id

    def fetch(self):
        return []


class LegacyRunIdOnlyScraper:
    def __init__(self, *, run_id: str | None = None) -> None:
        self.run_id = run_id

    def fetch(self):
        return []


class _OptionsOnlyBase:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options


class KwargsPassthroughOptionsScraper(_OptionsOnlyBase):
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        super().__init__(**kwargs)

    def fetch(self):
        return []


def test_factory_creates_new_style_scraper_with_options() -> None:
    run_config = RunConfig(include_urls=False, http_timeout=21)

    scraper = ScraperFactory().create(
        scraper_cls=NewStyleScraper,
        run_config=run_config,
        run_id="run-1",
    )

    assert isinstance(scraper.options, ScraperOptions)
    assert scraper.options.include_urls is False
    assert scraper.options.http.timeout == 21
    assert scraper.options.run_id == "run-1"
    assert scraper.run_id == "run-1"


def test_factory_creates_legacy_scraper_with_include_urls() -> None:
    run_config = RunConfig(include_urls=False)

    scraper = ScraperFactory().create(
        scraper_cls=LegacyScraper,
        run_config=run_config,
        run_id="legacy-run",
    )

    assert scraper.include_urls is False
    assert scraper.run_id == "legacy-run"


def test_factory_creates_legacy_scraper_without_include_urls_when_disabled() -> None:
    run_config = RunConfig(include_urls=False)

    scraper = ScraperFactory().create(
        scraper_cls=LegacyRunIdOnlyScraper,
        run_config=run_config,
        run_id="legacy-run-id",
        supports_urls=False,
    )

    assert scraper.run_id == "legacy-run-id"


def test_factory_does_not_inject_run_id_for_kwargs_passthrough_options_scraper() -> None:
    run_config = RunConfig(include_urls=False)

    scraper = ScraperFactory().create(
        scraper_cls=KwargsPassthroughOptionsScraper,
        run_config=run_config,
        run_id="run-id-from-factory",
    )

    assert "run_id" not in scraper.kwargs
    assert isinstance(scraper.options, ScraperOptions)
    assert scraper.options.run_id == "run-id-from-factory"


class _AlwaysAdapter:
    def __init__(self, marker: object) -> None:
        self._marker = marker

    def supports(self, _ctor) -> bool:
        return True

    def create(self, *, context, ctor):
        return context.scraper_cls(options=ScraperOptions(), marker=self._marker)


class CustomChainScraper:
    def __init__(self, *, options: ScraperOptions, marker: object) -> None:
        self.options = options
        self.marker = marker


def test_factory_uses_injected_adapters() -> None:
    marker = object()
    factory = ScraperFactory(adapters=(_AlwaysAdapter(marker),))

    scraper = factory.create(
        scraper_cls=CustomChainScraper,
        run_config=RunConfig(),
        run_id="chain",
    )

    assert scraper.marker is marker
