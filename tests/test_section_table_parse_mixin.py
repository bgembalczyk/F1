# ruff: noqa: ARG002, ARG005, EM101, N801, SLF001, TRY003
from types import SimpleNamespace

import pytest

from scrapers.base.mixins.section_table_parse import DeclarativeSectionTableParseMixin
from scrapers.base.mixins.section_table_parse import SectionTableParseMixin
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin


class _BaseScraper:
    def __init__(self, section_id="Section"):
        self.config = SimpleNamespace(section_id=section_id)
        self.include_urls = False
        self.normalize_empty_values = True

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


class _DeclarativeScraper(DeclarativeSectionTableParseMixin, _BaseScraper):
    domain = "constructors"
    section_label = "Current constructors"

    class section_parser_class:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def parse(self, _fragment):
            class _Result:
                records = ["parsed"]

            return _Result()


def test_declarative_parse_soup_delegates_to_base_logic(monkeypatch):
    scraper = _DeclarativeScraper(section_id="Known")

    monkeypatch.setattr(
        WikipediaSectionByIdMixin,
        "extract_section_by_id",
        staticmethod(lambda soup, section_id, *, domain=None: object()),
    )

    assert scraper._parse_soup(object()) == ["parsed"]


def test_declarative_parser_receives_unified_constructor_kwargs(monkeypatch):
    captured = {}

    class _Parser:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def parse(self, _fragment):
            class _Result:
                records = []

            return _Result()

    class _Scraper(DeclarativeSectionTableParseMixin, _BaseScraper):
        domain = "circuits"
        section_label = "Circuits"
        section_parser_class = _Parser

    scraper = _Scraper(section_id="Known")
    scraper.include_urls = True
    scraper.normalize_empty_values = False

    monkeypatch.setattr(
        WikipediaSectionByIdMixin,
        "extract_section_by_id",
        staticmethod(lambda soup, section_id, *, domain=None: object()),
    )

    scraper._parse_soup(object())

    assert captured["config"] is scraper.config
    assert captured["section_label"] == "Circuits"
    assert captured["include_urls"] is True
    assert captured["normalize_empty_values"] is False
