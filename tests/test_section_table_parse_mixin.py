from types import SimpleNamespace

import pytest

from scrapers.base.mixins.section_table_parse import SectionTableParseMixin
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin


class _BaseScraper:
    def __init__(self, section_id="Section"):
        self.config = SimpleNamespace(section_id=section_id)

    def _parse_soup(self, soup):
        return ["fallback"]


class _Scraper(SectionTableParseMixin, _BaseScraper):
    pass


def test_parse_section_or_fallback_raises_with_unified_context(monkeypatch):
    scraper = _Scraper(section_id="Missing")

    monkeypatch.setattr(
        WikipediaSectionByIdMixin,
        "extract_section_by_id",
        staticmethod(lambda soup, section_id, *, domain=None: None),
    )

    with pytest.raises(
        RuntimeError,
        match="domain='constructors', section_label='Current constructors'",
    ):
        scraper.parse_section_or_fallback(
            object(),
            domain="constructors",
            section_label="Current constructors",
            parser_factory=lambda: object(),
        )


def test_parse_section_or_fallback_uses_legacy_fallback_on_parser_error(monkeypatch):
    scraper = _Scraper(section_id="Known")

    monkeypatch.setattr(
        WikipediaSectionByIdMixin,
        "extract_section_by_id",
        staticmethod(lambda soup, section_id, *, domain=None: object()),
    )

    class _Parser:
        def parse(self, _fragment):
            raise RuntimeError("parser error")

    records = scraper.parse_section_or_fallback(
        object(),
        domain="circuits",
        parser_factory=lambda: _Parser(),
    )

    assert records == ["fallback"]


def test_parse_section_or_fallback_uses_legacy_flow_when_no_section_id():
    scraper = _Scraper(section_id=None)

    records = scraper.parse_section_or_fallback(
        object(),
        domain="circuits",
        parser_factory=lambda: object(),
    )

    assert records == ["fallback"]
