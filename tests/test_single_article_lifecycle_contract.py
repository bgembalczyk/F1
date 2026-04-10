from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scrapers.dto import InfoboxPayloadDTO
from scrapers.dto import SectionsPayloadDTO
from scrapers.dto import TablesPayloadDTO
from scrapers.single_wiki_article.single_article_domain_pipeline_base import (
    SingleArticleDomainPipelineBase,
)


class _LifecycleScraper(SingleArticleDomainPipelineBase):
    def __init__(self) -> None:
        super().__init__()
        self.hooks: list[str] = []

    def _before_payload_build(self, soup: BeautifulSoup) -> None:
        _ = soup
        self.hooks.append("before")

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        _ = soup
        self.hooks.append("infobox")
        return InfoboxPayloadDTO({"kind": "infobox"})

    def _build_tables_payload(self, soup: BeautifulSoup) -> TablesPayloadDTO:
        _ = soup
        self.hooks.append("tables")
        return TablesPayloadDTO([{"kind": "table"}])

    def _build_sections_payload(self, soup: BeautifulSoup) -> SectionsPayloadDTO:
        _ = soup
        self.hooks.append("sections")
        return SectionsPayloadDTO([{"kind": "section"}])

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, Any]:
        _ = soup
        self.hooks.append("assemble")
        return {
            "infobox": infobox_payload.data,
            "tables": tables_payload.data,
            "sections": sections_payload.data,
        }

    def _after_record_assembled(
        self,
        record: dict[str, Any],
        soup: BeautifulSoup,
    ) -> dict[str, Any]:
        _ = soup
        self.hooks.append("after")
        record["after"] = True
        return record


class _StrategyStub:
    def split_url_fragment(self, url: str) -> tuple[str, str | None]:
        return url.split("#", maxsplit=1)[0], "history"

    def select_article_soup(
        self,
        soup: BeautifulSoup,
        *,
        fragment: str | None,
    ) -> BeautifulSoup:
        return BeautifulSoup(f"<div data-fragment='{fragment}'></div>", "html.parser")

    def extract_section_by_id(
        self,
        soup: BeautifulSoup,
        section_id: str,
        *,
        domain: str | None = None,
    ) -> BeautifulSoup | None:
        _ = soup, section_id, domain
        return BeautifulSoup("<section></section>", "html.parser")


class _SectionAwareScraper(SingleArticleDomainPipelineBase):
    def __init__(self) -> None:
        super().__init__(section_selection_strategy=_StrategyStub())

    def fetch(self) -> list[dict[str, Any]]:
        return [{"url": self.url, "fragment": self._section_fragment}]

    def _assemble_record(self, **_kwargs) -> dict[str, Any]:
        return {"ok": True}


def test_lifecycle_contract_keeps_hook_order() -> None:
    scraper = _LifecycleScraper()

    result = scraper.parse(BeautifulSoup("<html></html>", "html.parser"))

    assert scraper.hooks == [
        "before",
        "infobox",
        "tables",
        "sections",
        "assemble",
        "after",
    ]
    assert result == [
        {
            "infobox": {"kind": "infobox"},
            "tables": [{"kind": "table"}],
            "sections": [{"kind": "section"}],
            "after": True,
        },
    ]


def test_lifecycle_contract_uses_parser_before_pipeline_fallback() -> None:
    scraper = _LifecycleScraper()

    class _ParserStub:
        def parse(self, _soup: BeautifulSoup) -> list[dict[str, str]]:
            return [{"source": "parser"}]

    scraper.parser = _ParserStub()

    result = scraper.parse(BeautifulSoup("<html></html>", "html.parser"))

    assert result == [{"source": "parser"}]
    assert scraper.hooks == []


def test_lifecycle_contract_handles_section_fragment_strategy() -> None:
    scraper = _SectionAwareScraper()

    fetched = scraper.extract_by_url("https://example.com/wiki/Foo#History")
    scoped_soup = scraper._prepare_article_soup(BeautifulSoup("<html></html>", "html.parser"))

    assert fetched == [{"url": "https://example.com/wiki/Foo", "fragment": "history"}]
    assert scoped_soup.find("div")["data-fragment"] == "history"
