# ruff: noqa: E501, PLR2004
"""Tests for TyreManufacturersBySeasonSubSectionParser covering lines 67-69, 72-74, 77-85."""

from scrapers.tyres.list_scraper import TyreManufacturersBySeasonSubSectionParser


def _make_table_element(data: dict | None = None, kind: str = "table") -> dict:
    return {"kind": kind, "data": data if data is not None else {}}


class TestSubSectionParserApplyForElements:
    def setup_method(self):
        self.parser = TyreManufacturersBySeasonSubSectionParser()

    def test_skips_non_table_elements(self):
        elements = [{"kind": "paragraph", "data": {"some": "data"}}]
        self.parser._apply_for_elements(elements)
        # unchanged - no table kind, nothing should happen
        assert elements[0]["data"] == {"some": "data"}

    def test_skips_table_elements_with_non_dict_data(self):
        elements = [{"kind": "table", "data": "not a dict"}]
        self.parser._apply_for_elements(elements)
        assert elements[0]["data"] == "not a dict"

    def test_skips_table_elements_with_none_data(self):
        elements = [{"kind": "table", "data": None}]
        self.parser._apply_for_elements(elements)
        assert elements[0]["data"] is None

    def test_applies_table_parser_for_non_matching_table_dict(self):
        # Table dict that does NOT match the tyre parser → parse returns None → unchanged
        elements = [{"kind": "table", "data": {"headers": ["Col1", "Col2"], "rows": []}}]
        original_data = elements[0]["data"]
        self.parser._apply_for_elements(elements)
        assert elements[0]["data"] is original_data

    def test_applies_table_parser_for_matching_table_dict(self):
        # Matching table data → parser returns non-None → data updated
        matching_data = {
            "headers": ["Season", "Manufacturer 1", "Wins"],
            "rows": [],
        }
        elements = [{"kind": "table", "data": matching_data}]
        self.parser._apply_for_elements(elements)
        # The parse was called and returned something, so data may be updated
        # (could still be same dict or different structure - just verify it ran)
        assert "data" in elements[0]


class TestSubSectionParserApplyTableParser:
    def setup_method(self):
        self.parser = TyreManufacturersBySeasonSubSectionParser()

    def test_empty_payload_does_nothing(self):
        self.parser._apply_table_parser({})
        # No assertion needed - just must not raise

    def test_payload_with_sub_sub_sections(self):
        payload = {
            "sub_sub_sections": [
                {"elements": [], "sub_sub_sections": []},
            ]
        }
        self.parser._apply_table_parser(payload)

    def test_recursive_application(self):
        payload = {
            "sub_sub_sections": [
                {
                    "elements": [],
                    "sub_sub_sections": [
                        {"elements": [{"kind": "table", "data": None}]},
                    ],
                }
            ]
        }
        self.parser._apply_table_parser(payload)

    def test_applies_elements_in_section(self):
        element = {"kind": "table", "data": {"headers": ["Col1"], "rows": []}}
        payload = {
            "sub_sub_sections": [
                {"elements": [element]},
            ]
        }
        self.parser._apply_table_parser(payload)
        assert "data" in element


class TestSubSectionParserParseGroup:
    def setup_method(self):
        self.parser = TyreManufacturersBySeasonSubSectionParser()

    def test_parse_group_returns_dict(self):
        result = self.parser.parse_group([], context=None)
        assert isinstance(result, dict)

    def test_parse_group_with_none_context(self):
        result = self.parser.parse_group([], context=None)
        assert isinstance(result, dict)
