from __future__ import annotations

from scrapers.base.abc import ABCScraper
from scrapers.base.domain_entrypoint import EagerScraperClassProvider
from scrapers.base.domain_entrypoint import LazyScraperClassProxy
from scrapers.base.domain_entrypoint import ScraperClassProviderProtocol


class _ContractDummyScraper(ABCScraper):
    pass


def test_lazy_provider_implements_provider_contract() -> None:
    provider: ScraperClassProviderProtocol = LazyScraperClassProxy(
        "scrapers.drivers.list_scraper:F1DriversListScraper",
    )
    resolved = provider.resolve()
    assert issubclass(resolved, ABCScraper)


def test_lazy_provider_resolves_once_and_caches_class(monkeypatch) -> None:
    calls: list[str] = []

    def fake_import_target(path: str) -> type[ABCScraper]:
        calls.append(path)
        return _ContractDummyScraper

    monkeypatch.setattr("scrapers.base.domain_entrypoint._import_target", fake_import_target)

    provider = LazyScraperClassProxy("irrelevant.path:Dummy")

    assert provider.resolve() is _ContractDummyScraper
    assert provider.resolve() is _ContractDummyScraper
    assert calls == ["irrelevant.path:Dummy"]


def test_eager_provider_implements_provider_contract() -> None:
    provider: ScraperClassProviderProtocol = EagerScraperClassProvider(
        _ContractDummyScraper,
    )
    assert provider.resolve() is _ContractDummyScraper
