# ruff: noqa: PLR2004
from collections.abc import Sequence

import pytest

from scrapers.base.factory.constructor_introspection import ConstructorIntrospection
from scrapers.base.factory.creation_adapter_protocol import (
    ScraperCreationAdapterProtocol,
)
from scrapers.base.factory.creation_context import ScraperCreationContext
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


class _AdapterStub(ScraperCreationAdapterProtocol):
    def __init__(
        self,
        *,
        name: str,
        supports_result: bool,
        calls: list[str],
    ) -> None:
        self._name = name
        self._supports_result = supports_result
        self._calls = calls

    def supports(self, _ctor: ConstructorIntrospection) -> bool:
        self._calls.append(f"supports:{self._name}")
        return self._supports_result

    def create(
        self,
        *,
        context: ScraperCreationContext,
        ctor: ConstructorIntrospection,
    ) -> NewStyleScraper:
        self._calls.append(f"create:{self._name}")
        return NewStyleScraper(
            options=ScraperOptions(),
            run_id=f"{context.run_id}:{ctor.accepts('options')}",
        )


def _build_factory_with_adapters(
    adapters: Sequence[ScraperCreationAdapterProtocol],
) -> ScraperFactory:
    return ScraperFactory(adapters=adapters)


def test_factory_selects_first_supporting_adapter() -> None:
    calls: list[str] = []
    first = _AdapterStub(name="first", supports_result=False, calls=calls)
    second = _AdapterStub(name="second", supports_result=True, calls=calls)
    third = _AdapterStub(name="third", supports_result=True, calls=calls)
    run_config = RunConfig()

    scraper = _build_factory_with_adapters([first, second, third]).create(
        scraper_cls=NewStyleScraper,
        run_config=run_config,
        run_id="run-di",
    )

    assert scraper.run_id == "run-di:True"
    assert calls == [
        "supports:first",
        "supports:second",
        "create:second",
    ]


def test_factory_checks_adapters_in_declared_order() -> None:
    calls: list[str] = []
    adapters = [
        _AdapterStub(name="a", supports_result=False, calls=calls),
        _AdapterStub(name="b", supports_result=False, calls=calls),
    ]

    with pytest.raises(TypeError, match="No adapter available"):
        _build_factory_with_adapters(adapters).create(
            scraper_cls=NewStyleScraper,
            run_config=RunConfig(),
            run_id="run-order",
        )

    assert calls == ["supports:a", "supports:b"]
