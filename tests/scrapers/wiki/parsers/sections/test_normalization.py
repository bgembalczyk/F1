# ruff: noqa: E501, PLR2004
"""Tests for normalize_section_text covering lines 9-10, 12-13."""

import pytest

from scrapers.parsers.section.wiki.normalization import normalize_section_text


class TestNormalizeSectionText:
    def test_none_raises_value_error(self):
        with pytest.raises(ValueError, match="Section text cannot be None"):
            normalize_section_text(None)  # type: ignore[arg-type]

    def test_non_string_raises_type_error(self):
        with pytest.raises(TypeError, match="Section text must be a string"):
            normalize_section_text(123)  # type: ignore[arg-type]

    def test_underscores_replaced_with_spaces(self):
        result = normalize_section_text("Race_Results")
        assert "_" not in result
        assert "race results" in result

    def test_lowercased(self):
        result = normalize_section_text("Constructor Standings")
        assert result == "constructor standings"

    def test_empty_string(self):
        result = normalize_section_text("")
        assert result == ""

    def test_strips_whitespace(self):
        result = normalize_section_text("  Season Results  ")
        assert result == "season results"
