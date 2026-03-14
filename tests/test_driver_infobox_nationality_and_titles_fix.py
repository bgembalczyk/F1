"""Tests for nationality link extraction and championship titles order preservation."""
# ruff: noqa: E501

import pytest
from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.drivers.infobox.scraper import DriverInfoboxScraper

EXPECTED_NATIONALITY_COUNT = 1
EXPECTED_TITLES_IN_LIST = 3
YEAR_2022 = 2022
YEAR_2009 = 2009
YEAR_2007 = 2007


@pytest.fixture()
def scraper():
    """Create a scraper instance with URL extraction enabled."""
    options = ScraperOptions(include_urls=True)
    return DriverInfoboxScraper(options=options)


def test_nationality_with_link(scraper):
    """Test nationality parsing with link extraction.

    This test verifies that when nationality has a link in the HTML,
    the parser extracts it as a dict with text and url fields.
    """
    html = """
    <table class="infobox vcard">
        <tr>
            <th colspan="2" class="infobox-header" style="background-color: gainsboro;">
                Formula One career
            </th>
        </tr>
        <tr><th scope="row" class="infobox-label">Nationality</th>
        <td class="infobox-data">
            <span class="flagicon">
                <span class="mw-image-border" typeof="mw:File">
                    <a href="/wiki/United_Kingdom" title="United Kingdom">
                        <img alt="United Kingdom"
                             src="//upload.wikimedia.org/wikipedia/en/thumb/a/ae/Flag_of_the_United_Kingdom.svg/40px-Flag_of_the_United_Kingdom.svg.png"
                             decoding="async"
                             width="23"
                             height="12"
                             class="mw-file-element"
                             srcset="//upload.wikimedia.org/wikipedia/en/thumb/a/ae/Flag_of_the_United_Kingdom.svg/60px-Flag_of_the_United_Kingdom.svg.png 2x"
                             data-file-width="1200"
                             data-file-height="600">
                    </a>
                </span>
            </span>
            <a href="/wiki/Formula_One_drivers_from_the_United_Kingdom"
               title="Formula One drivers from the United Kingdom">British</a>
        </td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = scraper.parse(soup)

    assert len(result) == 1
    assert "career" in result[0]
    assert len(result[0]["career"]) > 0

    # Find the "Nationality" row
    nationality_row = None
    for row in result[0]["career"][0]["rows"]:
        if row.get("label") == "Nationality":
            nationality_row = row
            break

    assert nationality_row is not None, "Nationality row not found"

    value = nationality_row["value"]
    assert isinstance(value, list), "Nationality value should be a list"
    assert len(value) == EXPECTED_NATIONALITY_COUNT

    nationality_item = value[0]
    assert isinstance(
        nationality_item,
        dict,
    ), "Nationality item should be a dict with text and url"
    assert "text" in nationality_item, "Nationality dict should have 'text' field"
    assert "url" in nationality_item, "Nationality dict should have 'url' field"
    assert nationality_item["text"] == "British"
    assert "Formula_One_drivers_from_the_United_Kingdom" in nationality_item["url"]


def test_nationality_without_link(scraper):
    """Test nationality parsing when there's no link (plain text).

    This test verifies backward compatibility - when there's no link,
    the parser should still work and return plain text strings.
    """
    html = """
    <table class="infobox vcard">
        <tr>
            <th colspan="2" class="infobox-header" style="background-color: gainsboro;">
                Formula One career
            </th>
        </tr>
        <tr><th scope="row" class="infobox-label">Nationality</th>
        <td class="infobox-data">American or Italian</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = scraper.parse(soup)

    assert len(result) == 1
    assert "career" in result[0]

    # Find the "Nationality" row
    nationality_row = None
    for row in result[0]["career"][0]["rows"]:
        if row.get("label") == "Nationality":
            nationality_row = row
            break

    assert nationality_row is not None
    value = nationality_row["value"]
    assert value == ["American", "Italian"]


def test_championship_titles_document_order(scraper):
    """Test championship titles preserve document order from list items.

    This test verifies that when years and titles are in <li> list items,
    the parser preserves their document order instead of sorting them.

    The HTML has years in order: 2022, 2009, 2007
    And titles in order: Indianapolis 500, Japanese F3, Formula BMW UK

    Expected pairing:
    - Indianapolis 500 -> 2022
    - Japanese F3 -> 2009
    - Formula BMW UK -> 2007
    """
    html = """
    <table class="infobox vcard">
        <tr>
            <th colspan="2" class="infobox-header" style="background-color: gainsboro;">
                Championship titles
            </th>
        </tr>
        <tr>
            <th scope="row" class="infobox-label">
                <link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r1126788409">
                <div class="plainlist">
                    <ul>
                        <li><a href="/wiki/2022_Indianapolis_500" title="2022 Indianapolis 500">2022</a></li>
                        <li><a href="/wiki/2009_All-Japan_Formula_Three_Championship"
                               class="mw-redirect"
                               title="2009 All-Japan Formula Three Championship">2009</a></li>
                        <li><a href="/wiki/2007_Formula_BMW_UK_season"
                               title="2007 Formula BMW UK season">2007</a></li>
                    </ul>
                </div>
            </th>
            <td class="infobox-data">
                <link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r1126788409">
                <div class="plainlist">
                    <ul>
                        <li><a href="/wiki/Indianapolis_500" title="Indianapolis 500">Indianapolis 500</a></li>
                        <li><a href="/wiki/Japanese_F3" class="mw-redirect" title="Japanese F3">Japanese F3</a></li>
                        <li><a href="/wiki/Formula_BMW" title="Formula BMW">Formula BMW UK</a></li>
                    </ul>
                </div>
            </td>
        </tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = scraper.parse(soup)

    assert len(result) == 1
    assert "championship_titles" in result[0]

    titles = result[0]["championship_titles"]
    assert len(titles) == EXPECTED_TITLES_IN_LIST

    # Verify the correct pairing (document order, not sorted order)
    assert titles[0]["title"]["text"] == "Indianapolis 500"
    assert titles[0]["years"][0]["year"] == YEAR_2022
    assert "2022_Indianapolis_500" in titles[0]["years"][0]["url"]

    assert titles[1]["title"]["text"] == "Japanese F3"
    assert titles[1]["years"][0]["year"] == YEAR_2009
    assert "2009_All-Japan_Formula_Three_Championship" in titles[1]["years"][0]["url"]

    assert titles[2]["title"]["text"] in [
        "Formula BMW",
        "Formula BMW UK",
    ]  # Link text may vary
    assert titles[2]["years"][0]["year"] == YEAR_2007
    assert "2007_Formula_BMW_UK_season" in titles[2]["years"][0]["url"]


def test_championship_titles_sorted_for_non_list(scraper):
    """Test that championship titles are still sorted when not in list items.

    This test verifies backward compatibility - when years are in plain text
    (not in list items), they should still be sorted as before.
    """
    html = """
    <table class="infobox vcard">
        <tr>
            <th colspan="2" class="infobox-header" style="background-color: gainsboro;">
                Championship titles
            </th>
        </tr>
        <tr>
            <th scope="row" class="infobox-label">
                <a href="/wiki/1981_Japanese_Formula_Two_Championship" class="new">1981</a>-<a href="/wiki/1982_Japanese_Formula_Two_Championship" class="new">1982</a>,<br>
                <a href="/wiki/1984_Japanese_Formula_Two_Championship" class="new">1984</a>-<a href="/wiki/1986_Japanese_Formula_Two_Championship">1986</a>
            </th>
            <td class="infobox-data">
                <a href="/wiki/Super_Formula" class="mw-redirect" title="Super Formula">
                    Japanese Formula Two
                </a>
            </td>
        </tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = scraper.parse(soup)

    assert len(result) == 1
    assert "championship_titles" in result[0]

    titles = result[0]["championship_titles"]
    assert len(titles) == 1

    champ = titles[0]
    assert champ["title"]["text"] == "Japanese Formula Two"

    # Years should be expanded and sorted: 1981, 1982, 1984, 1985, 1986
    years = champ["years"]
    year_values = [y["year"] for y in years if "year" in y]
    assert year_values == [
        1981,
        1982,
        1984,
        1985,
        1986,
    ], "Years should be sorted when not in list items"
