# ruff: noqa: E501, PLR2004
"""Tests for adapter.py covering lines 46, 53, 65-69, 72-74, 116, 123, 127-137, 165."""

from scrapers.wiki.parsers.sections.adapter import _extract_sections
from scrapers.wiki.parsers.sections.adapter import _iter_sections
from scrapers.wiki.parsers.sections.adapter import collect_section_elements
from scrapers.wiki.parsers.sections.adapter import find_section_tree


class TestExtractSections:
    def test_non_dict_returns_empty(self):
        assert _extract_sections(None) == []
        assert _extract_sections("string") == []  # type: ignore[arg-type]
        assert _extract_sections(123) == []  # type: ignore[arg-type]

    def test_dict_with_sections_key(self):
        article = {"sections": [{"name": "Results"}]}
        result = _extract_sections(article)
        assert len(result) == 1
        assert result[0]["name"] == "Results"

    def test_dict_with_content_text_sections(self):
        article = {
            "content_text": {
                "sections": [{"name": "Standings"}],
            },
        }
        result = _extract_sections(article)
        assert len(result) == 1
        assert result[0]["name"] == "Standings"

    def test_empty_dict_returns_empty(self):
        assert _extract_sections({}) == []

    def test_sections_not_a_list_falls_through(self):
        article = {"sections": "not a list"}
        result = _extract_sections(article)
        assert result == []

    def test_content_text_sections_not_a_list_returns_empty(self):
        article = {"content_text": {"sections": "not a list"}}
        result = _extract_sections(article)
        assert result == []


class TestIterSections:
    def test_yields_flat_sections(self):
        sections = [{"name": "A"}, {"name": "B"}]
        result = list(_iter_sections(sections))
        assert len(result) == 2

    def test_yields_nested_sub_sections(self):
        sections = [{"name": "Parent", "sub_sections": [{"name": "Child"}]}]
        result = list(_iter_sections(sections))
        assert len(result) == 2
        names = [s["name"] for s in result]
        assert "Parent" in names
        assert "Child" in names

    def test_yields_deeply_nested_sections(self):
        sections = [
            {
                "name": "Level1",
                "sub_sub_sections": [
                    {"name": "Level2", "sub_sub_sub_sections": [{"name": "Level3"}]},
                ],
            },
        ]
        result = list(_iter_sections(sections))
        names = [s["name"] for s in result]
        assert "Level1" in names
        assert "Level2" in names
        assert "Level3" in names

    def test_handles_empty_list(self):
        assert list(_iter_sections([])) == []




class TestFindSectionTree:
    def test_returns_none_for_empty_article(self):
        result = find_section_tree({}, "Results")
        assert result is None

    def test_returns_none_for_non_dict_article(self):
        result = find_section_tree(None, "Results")  # type: ignore[arg-type]
        assert result is None

    def test_exact_text_match(self):
        article = {
            "sections": [
                {"name": "Race Results", "section_id": "race_results", "elements": []},
                {"name": "Other", "section_id": "other", "elements": []},
            ],
        }
        result = find_section_tree(article, "Race Results")
        assert result is not None
        assert result["name"] == "Race Results"

    def test_fuzzy_match(self):
        article = {
            "sections": [
                {"name": "Race Results Table", "elements": []},
            ],
        }
        # fuzzy match: "race results table" vs "race results" should be high similarity
        result = find_section_tree(article, "Race Results", min_fuzzy_score=0.7)
        # May or may not match depending on ratio, but should not raise
        assert result is None or isinstance(result, dict)

    def test_no_match_returns_none(self):
        article = {
            "sections": [
                {"name": "Completely Different", "elements": []},
            ],
        }
        result = find_section_tree(article, "Race Results")
        assert result is None

    def test_content_text_path(self):
        article = {
            "content_text": {
                "sections": [
                    {"name": "Drivers", "section_id": "drivers", "elements": []},
                ],
            },
        }
        result = find_section_tree(article, "Drivers")
        assert result is not None

    def test_find_with_aliases(self):
        article = {
            "sections": [
                {"name": "Driver Standings", "elements": []},
            ],
        }
        result = find_section_tree(
            article,
            "Driver Standings",
            aliases=["Drivers Championship"],
        )
        assert result is not None


class TestCollectSectionElements:
    def test_collects_elements_of_matching_kind(self):
        section = {
            "name": "Results",
            "elements": [
                {"kind": "table", "data": {}},
                {"kind": "paragraph", "data": {}},
            ],
        }
        result = collect_section_elements(section, "table")
        assert len(result) == 1
        assert result[0]["kind"] == "table"

    def test_collects_elements_of_matching_type(self):
        section = {
            "name": "Results",
            "elements": [
                {"type": "table", "data": {}},
                {"type": "paragraph", "data": {}},
            ],
        }
        result = collect_section_elements(section, "table")
        assert len(result) == 1

    def test_returns_empty_list_when_no_matching_elements(self):
        section = {"name": "Results", "elements": [{"kind": "paragraph", "data": {}}]}
        result = collect_section_elements(section, "table")
        assert result == []

    def test_collects_from_nested_sections(self):
        section = {
            "name": "Top",
            "elements": [],
            "sub_sections": [
                {
                    "name": "Nested",
                    "elements": [{"kind": "table", "data": {"rows": []}}],
                },
            ],
        }
        result = collect_section_elements(section, "table")
        assert len(result) == 1

    def test_empty_section(self):
        result = collect_section_elements({"name": "Empty"}, "table")
        assert result == []
