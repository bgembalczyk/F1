from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

import pytest
from bs4 import BeautifulSoup

from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.base.sections.service import BaseSectionExtractionService

_single_wiki_base = pytest.importorskip("scrapers.base.single_wiki_article.base")
_single_wiki_dto = pytest.importorskip("scrapers.base.single_wiki_article.dto")
SingleWikiArticleScraperBase = _single_wiki_base.SingleWikiArticleScraperBase
InfoboxPayloadDTO = _single_wiki_dto.InfoboxPayloadDTO
SectionsPayloadDTO = _single_wiki_dto.SectionsPayloadDTO
TablesPayloadDTO = _single_wiki_dto.TablesPayloadDTO

if TYPE_CHECKING:
    from scrapers.base.sections.interface import SectionParseResult


class _SectionAdapterContract(Protocol):
    def parse_sections(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[SectionParseResult]: ...


class _SectionServiceContract(Protocol):
    def build_entries(self) -> list[SectionAdapterEntry]: ...


class _ContractSingleScraper(SingleWikiArticleScraperBase):
    url = "https://example.com"

    def __init__(self) -> None:
        super().__init__()
        self.trace: list[str] = []

    def _before_payload_build(self, soup: BeautifulSoup) -> None:
        _ = soup
        self.trace.append("before")

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        _ = soup
        self.trace.append("infobox")
        return InfoboxPayloadDTO(data={"k": "v"})

    def _build_tables_payload(self, soup: BeautifulSoup) -> TablesPayloadDTO:
        _ = soup
        self.trace.append("tables")
        return TablesPayloadDTO(data=[{"row": 1}])

    def _build_sections_payload(self, soup: BeautifulSoup) -> SectionsPayloadDTO:
        _ = soup
        self.trace.append("sections")
        return SectionsPayloadDTO(data=[{"section_id": "history"}])

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, Any]:
        _ = soup
        self.trace.append("assemble")
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
        self.trace.append("after")
        record["done"] = True
        return record


@dataclass
class _AdapterStub(_SectionAdapterContract):
    sections: list[SectionParseResult]

    def parse_sections(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[SectionParseResult]:
        _ = soup
        _ = domain
        _ = entries
        return self.sections


class _SectionServiceContractStub(BaseSectionExtractionService, _SectionServiceContract):
    domain = "unit-test"

    def build_entries(self) -> list[SectionAdapterEntry]:
        return []


def test_single_wiki_article_scraper_base_pipeline_contract() -> None:
    scraper = _ContractSingleScraper()
    result = scraper.parse(BeautifulSoup("<div></div>", "html.parser"))

    assert result == [
        {
            "infobox": {"k": "v"},
            "tables": [{"row": 1}],
            "sections": [{"section_id": "history"}],
            "done": True,
        },
    ]
    assert scraper.trace == [
        "before",
        "infobox",
        "tables",
        "sections",
        "assemble",
        "after",
    ]


def test_base_section_service_contract_requires_optional_dependencies() -> None:
    service = _SectionServiceContractStub(adapter=_AdapterStub(sections=[]))
    with pytest.raises(ValueError, match="requires ScraperOptions"):
        service.require_options()

    with pytest.raises(ValueError, match="requires a URL"):
        service.require_url()
