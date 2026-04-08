# ruff: noqa: E501, PLR2004
"""Tests for TyreManufacturersBySeasonSubSectionParser covering lines 67-69, 72-74, 77-85."""

from scrapers.tyres.list_scraper import TyreManufacturersBySeasonSubSectionParser


def make_table_element(data: dict | None = None, kind: str = "table") -> dict:
    return {"kind": kind, "data": data if data is not None else {}}


class TestSubSectionParserParseGroup:
    def setup_method(self):
        self.parser = TyreManufacturersBySeasonSubSectionParser()

    def test_parse_group_returns_dict(self):
        result = self.parser.parse_group([], context=None)
        assert isinstance(result, dict)

    def test_parse_group_with_none_context(self):
        result = self.parser.parse_group([], context=None)
        assert isinstance(result, dict)
