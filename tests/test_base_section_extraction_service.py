from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.service import BaseSectionExtractionService


class _AdapterStub:
    def __init__(self, sections: list[SectionParseResult]) -> None:
        self.sections = sections
        self.calls: list[tuple[str, list[object]]] = []

    def parse_sections(self, *, soup, domain, entries):
        self.calls.append((domain, entries))
        return self.sections


class _SectionServiceStub(BaseSectionExtractionService):
    domain = "unit"

    def build_entries(self) -> list[object]:
        return ["entry"]


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

    assert adapter.calls == [("unit", ["entry"])]
    assert result == [
        {
            "section_id": "history",
            "section_label": "History",
            "records": [{"year": 1950}],
            "metadata": {
                "parser": "StubParser",
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
                "section_id": "career",
                "section_label": "Career",
            },
        },
    ]
