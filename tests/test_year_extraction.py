import pytest
from scrapers.base.helpers.year_extraction import YearExtractor

def test_extract_years_from_text_individual():
    text = "In 2002 and 2005"
    assert YearExtractor.extract_years_from_text(text) == {2002, 2005}

def test_extract_years_from_text_range():
    text = "From 2007-2008"
    assert YearExtractor.extract_years_from_text(text) == {2007, 2008}

def test_extract_years_from_text_unicode_range():
    text = "From 2007\u20132009"
    assert YearExtractor.extract_years_from_text(text) == {2007, 2008, 2009}

def test_extract_years_from_text_short_range():
    text = "From 2018-19"
    assert YearExtractor.extract_years_from_text(text) == {2018, 2019}

def test_extract_years_from_text_mixed():
    text = "Years 2002, 2007-08, 2018-19 and 2021"
    assert YearExtractor.extract_years_from_text(text) == {2002, 2007, 2008, 2018, 2019, 2021}

def test_build_year_to_url_map():
    links = [
        {"text": "2002", "url": "https://en.wikipedia.org/wiki/2002"},
        {"text": "2005", "url": "https://en.wikipedia.org/wiki/2005"},
        {"text": "not a year", "url": "https://en.wikipedia.org/wiki/Other"},
    ]
    expected = {
        2002: "https://en.wikipedia.org/wiki/2002",
        2005: "https://en.wikipedia.org/wiki/2005",
    }
    assert YearExtractor.build_year_to_url_map(links) == expected

def test_detect_url_pattern():
    year_to_url = {
        2002: "https://en.wikipedia.org/wiki/2002_Season",
        2005: "https://en.wikipedia.org/wiki/2005_Season",
    }
    assert YearExtractor.detect_url_pattern(year_to_url) == "https://en.wikipedia.org/wiki/{year}_Season"

def test_interpolate_urls():
    years_set = {2002, 2003, 2004, 2005}
    year_to_url = {
        2002: "https://en.wikipedia.org/wiki/2002_Season",
        2005: "https://en.wikipedia.org/wiki/2005_Season",
    }
    result = YearExtractor.interpolate_urls(years_set, year_to_url)
    assert result[2003] == "https://en.wikipedia.org/wiki/2003_Season"
    assert result[2004] == "https://en.wikipedia.org/wiki/2004_Season"
    assert result[2002] == "https://en.wikipedia.org/wiki/2002_Season"
    assert result[2005] == "https://en.wikipedia.org/wiki/2005_Season"
