# ruff: noqa: E501, PLR2004
"""Tests for SponsorshipRecordText covering uncovered lines."""

import pytest

from scrapers.sponsorship_liveries.parsers.record_text import SponsorshipRecordText


class TestExpandYearRange:
    def test_start_less_than_end(self):
        result = SponsorshipRecordText._expand_year_range(1988, 1990)
        assert result == {1988, 1989, 1990}

    def test_start_equals_end(self):
        result = SponsorshipRecordText._expand_year_range(1990, 1990)
        assert result == {1990}

    def test_start_greater_than_end_returns_empty(self):
        result = SponsorshipRecordText._expand_year_range(1991, 1988)
        assert result == set()


class TestAbbrevEndYear:
    def test_same_century(self):
        result = SponsorshipRecordText._abbrev_end_year(1979, 83)
        assert result == 1983

    def test_century_crossing(self):
        result = SponsorshipRecordText._abbrev_end_year(1999, 3)
        assert result == 2003

    def test_exact_century_boundary(self):
        result = SponsorshipRecordText._abbrev_end_year(1997, 99)
        assert result == 1999


class TestExtractYearParams:
    def test_extracts_single_year(self):
        result = SponsorshipRecordText.extract_year_params([{"text": "1990"}])
        assert 1990 in result

    def test_extracts_full_year_range(self):
        result = SponsorshipRecordText.extract_year_params([{"text": "1988-1990"}])
        assert result == {1988, 1989, 1990}

    def test_extracts_abbreviated_year_range(self):
        result = SponsorshipRecordText.extract_year_params([{"text": "1979-83"}])
        assert result == {1979, 1980, 1981, 1982, 1983}

    def test_century_crossing_abbreviated_range(self):
        result = SponsorshipRecordText.extract_year_params([{"text": "1999-03"}])
        assert result == {1999, 2000, 2001, 2002, 2003}

    def test_plain_string_param(self):
        result = SponsorshipRecordText.extract_year_params(["2021"])
        assert 2021 in result

    def test_empty_list(self):
        result = SponsorshipRecordText.extract_year_params([])
        assert result == set()


class TestParamText:
    def test_dict_with_text(self):
        assert SponsorshipRecordText.param_text({"text": "Monaco Grand Prix"}) == "Monaco Grand Prix"

    def test_dict_without_text(self):
        assert SponsorshipRecordText.param_text({"url": "http://example.com"}) == ""

    def test_plain_string(self):
        assert SponsorshipRecordText.param_text("hello") == "hello"

    def test_none_becomes_empty(self):
        assert SponsorshipRecordText.param_text(None) == ""


class TestIsYearParam:
    def test_simple_year_is_year_param(self):
        assert SponsorshipRecordText.is_year_param("1990") is True

    def test_year_range_is_year_param(self):
        assert SponsorshipRecordText.is_year_param("1988-1990") is True

    def test_grand_prix_text_is_not_year_param(self):
        assert SponsorshipRecordText.is_year_param("Monaco Grand Prix") is False

    def test_empty_text_is_not_year_param(self):
        assert SponsorshipRecordText.is_year_param("") is False

    def test_dict_year_param(self):
        assert SponsorshipRecordText.is_year_param({"text": "1990"}) is True


class TestExtractYearsFromText:
    def test_extracts_year(self):
        result = SponsorshipRecordText.extract_years_from_text("Won in 1988")
        assert 1988 in result

    def test_extracts_decade(self):
        result = SponsorshipRecordText.extract_years_from_text("the 1980s era")
        assert 1980 in result
        assert 1989 in result

    def test_empty_text(self):
        result = SponsorshipRecordText.extract_years_from_text("")
        assert result == set()


class TestStripYearSuffix:
    def test_strips_year_in_parens(self):
        result = SponsorshipRecordText.strip_year_suffix("Monaco Grand Prix (1988)")
        assert "1988" not in result

    def test_strips_trailing_year(self):
        result = SponsorshipRecordText.strip_year_suffix("Monaco Grand Prix 1988")
        assert result == "Monaco Grand Prix"

    def test_no_year_returns_original(self):
        result = SponsorshipRecordText.strip_year_suffix("Monaco Grand Prix")
        assert result == "Monaco Grand Prix"


class TestStripYearsKeepContext:
    def test_strips_years_from_text(self):
        result = SponsorshipRecordText.strip_years_keep_context("Sponsor from 1988 to 1990")
        assert "1988" not in result
        assert "1990" not in result

    def test_strips_decade_from_text(self):
        result = SponsorshipRecordText.strip_years_keep_context("1980s sponsor")
        assert "1980s" not in result
