from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from bs4 import BeautifulSoup

from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.service import BaseSectionExtractionService


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


@dataclass
class _AdapterStub(_SectionAdapterContract):
    sections: list[SectionParseResult]

    def __post_init__(self) -> None:
        self.calls: list[tuple[str, list[SectionAdapterEntry]]] = []

    def parse_sections(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[SectionParseResult]:
        _ = soup
        self.calls.append((domain, entries))
        return self.sections


class _SectionServiceStub(BaseSectionExtractionService, _SectionServiceContract):
    domain = "unit"

    def build_entries(self) -> list[SectionAdapterEntry]:
        return [
            SectionAdapterEntry(section_id="entry", aliases=(), parser=_ParserOk()),
        ]


class _FlattenSectionServiceStub(_SectionServiceStub):
    flatten_records = True


def test_base_section_extraction_service_returns_normalized_section_payloads() -> None:
    adapter = _AdapterStub(
        [
            SectionParseResult(
                section_id="history",
                section_label="History",
                records=[{"year": 1950}],
                metadata={"parser": "StubParser"},
            ),
        ],
    )

    result = _SectionServiceStub(adapter=adapter).extract(
        BeautifulSoup("<div></div>", "html.parser"),
    )

    assert len(adapter.calls) == 1
    domain, entries = adapter.calls[0]
    assert domain == "unit"
    assert len(entries) == 1
    assert entries[0].section_id == "entry"
    assert entries[0].aliases == ()
    assert isinstance(entries[0].parser, _ParserOk)
    assert result == [
        {
            "section_id": "history",
            "section_label": "History",
            "records": [{"year": 1950}],
            "metadata": {
                "parser": "StubParser",
                "source": "unknown",
                "heading_path": [],
                "section_id": "history",
                "section_label": "History",
            },
        },
    ]


def test_base_section_extraction_service_flattens_records_with_section_metadata():
    adapter = _AdapterStub(
        [
            SectionParseResult(
                section_id="career",
                section_label="Career",
                records=[{"year": 1950}],
                metadata={"aliases": ["Career results"]},
            ),
        ],
    )

    result = _FlattenSectionServiceStub(adapter=adapter).extract(
        BeautifulSoup("<div></div>", "html.parser"),
    )

    assert result == [
        {
            "year": 1950,
            "section": "Career",
            "section_id": "career",
            "section_metadata": {
                "aliases": ["Career results"],
                "parser": "unknown",
                "source": "unknown",
                "heading_path": [],
                "section_id": "career",
                "section_label": "Career",
            },
        },
    ]


class _ParserOk:
    def parse(self, _fragment):
        return SectionParseResult(
            section_id="ok",
            section_label="OK",
            records=[{"v": 1}],
            metadata={"parser": "ok"},
        )


class _ParserFail:
    def parse(self, _fragment):
        msg = "boom"
        raise RuntimeError(msg)


class _AdapterPerEntryStub(_SectionAdapterContract):
    def parse_sections(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[SectionParseResult]:
        _ = soup, domain
        return [entries[0].parser.parse(None)]


class _ErrorTolerantService(BaseSectionExtractionService):
    domain = "unit"

    def build_entries(self) -> list[SectionAdapterEntry]:
        return [
            SectionAdapterEntry(section_id="ok", aliases=(), parser=_ParserOk()),
            SectionAdapterEntry(section_id="fail", aliases=(), parser=_ParserFail()),
        ]


def test_base_section_extraction_service_continues_when_single_parser_fails(caplog):
    result = _ErrorTolerantService(adapter=_AdapterPerEntryStub()).extract(
        BeautifulSoup("<div></div>", "html.parser"),
    )

    assert result == [
        {
            "section_id": "ok",
            "section_label": "OK",
            "records": [{"v": 1}],
            "metadata": {
                "parser": "ok",
                "source": "unknown",
                "heading_path": [],
                "section_id": "ok",
                "section_label": "OK",
            },
        },
    ]
    assert "Failed to parse section entry" in caplog.text
