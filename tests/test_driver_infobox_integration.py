"""Integration test for DriverInfoboxScraper with real-world HTML examples."""

import pytest
from bs4 import BeautifulSoup

from scrapers.drivers.infobox.scraper import DriverInfoboxScraper
from scrapers.base.options import ScraperOptions


@pytest.fixture
def scraper():
    """Create a DriverInfoboxScraper instance."""
    options = ScraperOptions(include_urls=True)
    return DriverInfoboxScraper(options=options)


def test_died_field_aged_filtering(scraper):
    """Test that (aged X) is filtered from died place."""
    html = """
    <table class="infobox vcard">
        <tr><th scope="row" class="infobox-label">Died</th>
        <td class="infobox-data">August 11, 2020<span style="display:none">(2020-08-11)</span> (aged&nbsp;89)<span style="display:none" data-plural="0"></span></td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = scraper.parse(soup)

    assert len(result) == 1
    assert "general" in result[0]
    assert "died" in result[0]["general"]
    died = result[0]["general"]["died"]
    assert died["date"] == "2020-08-11"
    # Place should be None or empty, not contain "(aged 89)"
    assert died["place"] is None or died["place"] == []


def test_best_finish_no_links(scraper):
    """Test best finish parsing without links."""
    html = """
    <table class="infobox vcard">
        <tr><th colspan="2" class="infobox-header" style="background-color: gainsboro;">Formula One career</th></tr>
        <tr><th scope="row" class="infobox-label"><abbr title="Best season finish in the championship">Best finish</abbr></th>
        <td class="infobox-data">1st in 1957</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = scraper.parse(soup)

    assert len(result) == 1
    assert "career" in result[0]
    assert len(result[0]["career"]) > 0

    # Find the "Best finish" row
    for row in result[0]["career"][0]["rows"]:
        if row.get("label") == "Best finish":
            value = row["value"]
            assert value["result"] == "1st"
            assert value["seasons"] == [1957]
            return

    pytest.fail("Best finish row not found")


def test_championship_titles_with_year_ranges(scraper):
    """Test championship titles with year ranges expanded."""
    html = """
    <table class="infobox vcard">
        <tr><th colspan="2" class="infobox-header" style="background-color: gainsboro;">Championship titles</th></tr>
        <tr><th scope="row" class="infobox-label">
            <a href="/w/index.php?title=1981_Japanese_Formula_Two_Championship&amp;action=edit&amp;redlink=1" class="new">1981</a>–<a href="/w/index.php?title=1982_Japanese_Formula_Two_Championship&amp;action=edit&amp;redlink=1" class="new">1982</a>,<br>
            <a href="/w/index.php?title=1984_Japanese_Formula_Two_Championship&amp;action=edit&amp;redlink=1" class="new">1984</a>–<a href="/wiki/1986_Japanese_Formula_Two_Championship" title="1986 Japanese Formula Two Championship">1986</a>
        </th>
        <td class="infobox-data"><a href="/wiki/Super_Formula" class="mw-redirect" title="Super Formula">Japanese Formula Two</a></td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = scraper.parse(soup)

    assert len(result) == 1
    assert "championship_titles" in result[0]
    assert len(result[0]["championship_titles"]) > 0

    # Check that years are expanded
    champ = result[0]["championship_titles"][0]
    assert champ["title"]["text"] == "Japanese Formula Two"

    # Years should be: 1981, 1982, 1984, 1985, 1986
    years = champ["years"]
    year_values = [y["year"] for y in years if "year" in y]
    assert 1981 in year_values
    assert 1982 in year_values
    assert 1984 in year_values
    assert 1985 in year_values
    assert 1986 in year_values


def test_nationality_with_or(scraper):
    """Test nationality parsing with 'or' separator."""
    html = """
    <table class="infobox vcard">
        <tr><th colspan="2" class="infobox-header" style="background-color: gainsboro;">Formula One career</th></tr>
        <tr><th scope="row" class="infobox-label">Nationality</th>
        <td class="infobox-data">American or Italian</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = scraper.parse(soup)

    assert len(result) == 1
    assert "career" in result[0]
    assert len(result[0]["career"]) > 0

    # Find the "Nationality" row
    for row in result[0]["career"][0]["rows"]:
        if row.get("label") == "Nationality":
            value = row["value"]
            assert value == ["American", "Italian"]
            return

    pytest.fail("Nationality row not found")


def test_major_victories_from_championship_section(scraper):
    """Test parsing major victories from Championship titles section."""
    html = """
    <table class="infobox vcard">
        <tr><th colspan="2" class="infobox-header" style="background-color: gainsboro;">Championship titles</th></tr>
        <tr><td colspan="2" class="infobox-full-data"><b>Major victories</b> <br> 
        <a href="/wiki/24_Hours_of_Le_Mans" title="24 Hours of Le Mans">24 Hours of Le Mans</a> 
        (<a href="/wiki/1934_24_Hours_of_Le_Mans" title="1934 24 Hours of Le Mans">1934</a>)</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = scraper.parse(soup)

    assert len(result) == 1
    assert "major_victories" in result[0]
    assert len(result[0]["major_victories"]) > 0

    victory = result[0]["major_victories"][0]
    assert victory["title"]["text"] == "24 Hours of Le Mans"
    assert len(victory["years"]) == 1
    assert victory["years"][0]["text"] == "1934"


def test_full_data_table_top_tens(scraper):
    """Test full data table with Top tens column."""
    html = """
    <table class="infobox vcard">
        <tr><th colspan="2" class="infobox-header" style="background-color: gainsboro;">Formula One career</th></tr>
        <tr><td colspan="2" class="infobox-full-data">
            <table style="width:100%;">
                <tbody>
                    <tr>
                        <th>Wins</th>
                        <th>Top tens</th>
                        <th>Poles</th>
                    </tr>
                    <tr>
                        <td>7</td>
                        <td>11</td>
                        <td>2</td>
                    </tr>
                </tbody>
            </table>
        </td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = scraper.parse(soup)

    assert len(result) == 1
    assert "career" in result[0]
    assert len(result[0]["career"]) > 0

    # Find the full_data row with stats
    for row in result[0]["career"][0]["rows"]:
        if "full_data" in row:
            data = row["full_data"]
            assert data["wins"] == 7
            assert data["top_tens"] == 11
            assert data["poles"] == 2
            return

    pytest.fail("Full data stats row not found")
