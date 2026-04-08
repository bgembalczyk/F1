"""Integration test for DriverInfoboxParser with real-world HTML examples."""
# ruff: noqa: E501, PT001

import pytest
from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.drivers.infobox.scraper import DriverInfoboxParser
from tests.support.driver_infobox_assertions import assert_career_parsed

EXPANDED_YEAR_VALUES = [1981, 1982, 1984, 1985, 1986]
EXPECTED_WINS = 7
EXPECTED_TOP_TENS = 11
EXPECTED_POLES = 2


@pytest.fixture()
def scraper():
    """Create a DriverInfoboxParser instance."""
    options = ScraperOptions(include_urls=True)
    return DriverInfoboxParser(options=options)


class TestDriverInfoboxIntegration:
    def _parse_and_validate(self, scraper, html, section_key):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        result = scraper.parse(table)

        assert len(result) == 1
        assert section_key in result[0]
        assert len(result[0][section_key]) > 0
        return result

    def test_died_field_aged_filtering(self, scraper):
        """Test that (aged X) is filtered from died place."""
        html = """
        <table class="infobox vcard">
            <tr><th scope="row" class="infobox-label">Died</th>
            <td class="infobox-data">
                August 11, 2020<span style="display:none">(2020-08-11)</span>
                (aged&nbsp;89)<span style="display:none" data-plural="0"></span>
            </td></tr>
        </table>
        """
        result = self._parse_and_validate(scraper, html, "general")  # PRIVATE-API-JUSTIFIED
        assert "died" in result[0]["general"]
        died = result[0]["general"]["died"]
        assert died["date"] == "2020-08-11"
        # Place should be None or empty, not contain "(aged 89)"
        assert died["place"] is None or died["place"] == []

    def test_best_finish_no_links(self, scraper):
        """Test best finish parsing without links."""
        html = """
            <table class="infobox vcard">
                <tr>
                    <th colspan="2" class="infobox-header" style="background-color: gainsboro;">
                        Championship titles
                    </th>
                </tr>
                <tr><td colspan="2" class="infobox-full-data"><b>Major victories</b> <br>
                <a href="/wiki/24_Hours_of_Le_Mans" title="24 Hours of Le Mans">
                    24 Hours of Le Mans
                </a>
            </td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        result = scraper.parse(table)

        assert len(result) == 1
        assert "championship_titles" in result[0]
        assert len(result[0]["championship_titles"]) > 0

        # Check that years are expanded
        champ = result[0]["championship_titles"][0]
        assert champ["title"]["text"] == "Japanese Formula Two"

        # Years should be: 1981, 1982, 1984, 1985, 1986
        years = champ["years"]
        year_values = [y["year"] for y in years if "year" in y]
        for expected_year in EXPANDED_YEAR_VALUES:
            assert expected_year in year_values


    def test_major_victories_from_championship_section2(self, scraper):
        """Test parsing major victories from Championship titles section."""
        html = """
        <table class="infobox vcard">
            <tr>
                <th colspan="2" class="infobox-header" style="background-color: gainsboro;">
                    Formula One career
                </th>
            </tr>
            <tr><th scope="row" class="infobox-label">
                <abbr title="Best season finish in the championship">Best finish</abbr>
            </th>
        </tr>
            <tr><th scope="row" class="infobox-label">
                <abbr title="Best season finish in the championship">Best finish</abbr>
            </th>
            <td class="infobox-data">1st in 1957</td></tr>
        </table>
        """
        result = assert_career_parsed(scraper, html)

        # Find the "Best finish" row
        for row in result[0]["career"][0]["rows"]:
            if row.get("label") == "Best finish":
                value = row["value"]
                assert value["result"] == "1st"
                assert value["seasons"] == [1957]
                return

        pytest.fail("Best finish row not found")

    def test_championship_titles_with_year_ranges(self, scraper):
        """Test championship titles with year ranges expanded."""
        html = """
        <table class="infobox vcard">
            <tr>
                <th colspan="2" class="infobox-header" style="background-color: gainsboro;">
                    Championship titles
                </th>
                <td class="infobox-data">
                    <a href="/wiki/Super_Formula" class="mw-redirect" title="Super Formula">
                        Japanese Formula Two
                    </a>
                </td></tr>
            </table>
        """
        result = self._parse_and_validate(scraper, html, "championship_titles")  # PRIVATE-API-JUSTIFIED

        # Check that years are expanded
        champ = result[0]["championship_titles"][0]
        assert champ["title"]["text"] == "Japanese Formula Two"

        # Years should be: 1981, 1982, 1984, 1985, 1986
        years = champ["years"]
        year_values = [y["year"] for y in years if "year" in y]
        for expected_year in EXPANDED_YEAR_VALUES:
            assert expected_year in year_values

    def test_nationality_with_or(self, scraper):
        """Test nationality parsing with 'or' separator."""
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
        result = self._parse_and_validate(scraper, html, "career")  # PRIVATE-API-JUSTIFIED

        # Find the "Nationality" row
        for row in result[0]["career"][0]["rows"]:
            if row.get("label") == "Nationality":
                value = row["value"]
                assert value == ["American", "Italian"]
                return

        pytest.fail("Nationality row not found")

    def test_major_victories_from_championship_section(self, scraper):
        """Test parsing major victories from Championship titles section."""
        html = """
        <table class="infobox vcard">
            <tr>
                <th colspan="2" class="infobox-header" style="background-color: gainsboro;">
                    Championship titles
                </th>
            </tr>
            <tr><td colspan="2" class="infobox-full-data"><b>Major victories</b> <br>
            <a href="/wiki/24_Hours_of_Le_Mans" title="24 Hours of Le Mans">
                24 Hours of Le Mans
            </a>
            (<a href="/wiki/1934_24_Hours_of_Le_Mans" title="1934 24 Hours of Le Mans">
                1934
            </a>)</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        result = scraper.parse(table)

        assert len(result) == 1
        assert "major_victories" in result[0]
        assert len(result[0]["major_victories"]) > 0

        victory = result[0]["major_victories"][0]
        assert victory["title"]["text"] == "24 Hours of Le Mans"
        assert len(victory["years"]) == 1
        assert victory["years"][0]["text"] == "1934"


    def test_full_data_table_top_tens(self, scraper):
        """Test full data table with Top tens column."""
        html = """
        <table class="infobox vcard">
            <tr>
                <th colspan="2" class="infobox-header" style="background-color: gainsboro;">
                    Formula One career
                </th>
            </tr>
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
        result = assert_career_parsed(scraper, html)

        # Find the full_data row with stats
        for row in result[0]["career"][0]["rows"]:
            if "full_data" in row:
                data = row["full_data"]
                assert data["wins"] == EXPECTED_WINS
                assert data["top_tens"] == EXPECTED_TOP_TENS
                assert data["poles"] == EXPECTED_POLES
                return

        pytest.fail("Full data stats row not found")
