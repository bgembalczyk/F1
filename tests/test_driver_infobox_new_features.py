"""Tests for new driver infobox parser features."""

import pytest
from bs4 import BeautifulSoup

from scrapers.drivers.infobox.parsers.cell import InfoboxCellParser
from scrapers.drivers.infobox.parsers.general import InfoboxGeneralParser
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor
from scrapers.drivers.infobox.parsers.title import InfoboxTitlesParser


@pytest.fixture
def link_extractor():
    return InfoboxLinkExtractor(
        include_urls=True,
        wikipedia_base="https://en.wikipedia.org",
    )


@pytest.fixture
def cell_parser(link_extractor):
    return InfoboxCellParser(include_urls=True, link_extractor=link_extractor)


@pytest.fixture
def general_parser(link_extractor):
    return InfoboxGeneralParser(
        include_urls=True,
        link_extractor=link_extractor,
        schema=None,
        logger=None,
    )


@pytest.fixture
def titles_parser(link_extractor):
    return InfoboxTitlesParser(link_extractor)


class TestDiedFieldWithAge:
    """Tests for Died field parsing to exclude (aged X)."""

    def test_died_excludes_aged_from_place(self, general_parser):
        """Test that (aged 89) is excluded from place of death."""
        html = """<td class="infobox-data">August 11, 2020<span style="display:none">(2020-08-11)</span> (aged&nbsp;89)<span style="display:none" data-plural="0"></span></td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = general_parser._parse_date_place(cell)

        assert result["date"] == "2020-08-11"
        # Place should be None or empty, not contain "(aged 89)"
        assert result["place"] is None or result["place"] == []


class TestBestFinishWithoutLinks:
    """Tests for Best finish parsing without links."""

    def test_best_finish_single_year_no_links(self, cell_parser):
        """Test best finish with single year and no links: 1st in 1957."""
        html = """<td class="infobox-data">1st in 1957</td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_best_finish(cell)

        assert result["result"] == "1st"
        assert result["seasons"] == [1957]

    def test_best_finish_multiple_years_no_links(self, cell_parser):
        """Test best finish with multiple years and no links: 1st in 1952, 1954."""
        html = """<td class="infobox-data">1st in 1952, 1954</td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_best_finish(cell)

        assert result["result"] == "1st"
        assert result["seasons"] == [1952, 1954]


class TestChampionshipTitlesWithYearRanges:
    """Tests for Championship titles parsing with year ranges."""

    def test_championship_titles_expand_year_ranges(self, titles_parser):
        """Test that year ranges are expanded to individual years."""
        # Simulate a championship titles row
        html_label = """<th scope="row" class="infobox-label">
            <a href="/w/index.php?title=1981_Japanese_Formula_Two_Championship&amp;action=edit&amp;redlink=1" class="new">1981</a>–<a href="/w/index.php?title=1982_Japanese_Formula_Two_Championship&amp;action=edit&amp;redlink=1" class="new">1982</a>,<br>
            <a href="/w/index.php?title=1984_Japanese_Formula_Two_Championship&amp;action=edit&amp;redlink=1" class="new">1984</a>–<a href="/wiki/1986_Japanese_Formula_Two_Championship" title="1986 Japanese Formula Two Championship">1986</a>
        </th>"""
        html_value = """<td class="infobox-data">
            <a href="/wiki/Super_Formula" class="mw-redirect" title="Super Formula">Japanese Formula Two</a>
        </td>"""

        label_cell = BeautifulSoup(html_label, "html.parser").find("th")
        value_cell = BeautifulSoup(html_value, "html.parser").find("td")

        rows = [{"label_cell": label_cell, "value_cell": value_cell}]
        result = titles_parser.parse_titles(rows)

        assert len(result) == 1
        assert result[0]["title"]["text"] == "Japanese Formula Two"

        # Years should be expanded: 1981, 1982, 1984, 1985, 1986
        years = result[0]["years"]
        assert len(years) == 5

        # Extract year values
        year_values = [y["year"] for y in years if "year" in y]
        assert 1981 in year_values
        assert 1982 in year_values
        assert 1984 in year_values
        assert 1985 in year_values
        assert 1986 in year_values

        # Check that 1986 has a URL (it's the only one with a real link)
        year_1986 = next(y for y in years if y.get("year") == 1986)
        assert year_1986["url"] is not None
        assert "1986_Japanese_Formula_Two_Championship" in year_1986["url"]


class TestFullDataTableStats:
    """Tests for full data table statistics extraction."""

    def test_wins_top_tens_poles_table(self, cell_parser):
        """Test extraction of Wins, Top tens, Poles from table."""
        html = """<td colspan="2" class="infobox-full-data">
            <table style="width:100%; background-color: inherit; color:inherit;">
                <tbody>
                    <tr>
                        <th style="width: 33.3%; text-align: center; font-size: larger">Wins</th>
                        <th style="width: 33.3%; text-align: center; font-size: larger">Top tens</th>
                        <th style="width: 33.3%; text-align: center; font-size: larger">Poles</th>
                    </tr>
                    <tr>
                        <td style="text-align: center; font-size: larger">7</td>
                        <td style="text-align: center; font-size: larger">11</td>
                        <td style="text-align: center; font-size: larger">2</td>
                    </tr>
                </tbody>
            </table>
        </td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_full_data(cell)

        assert result["wins"] == 7
        assert result["top_tens"] == 11
        assert result["poles"] == 2
        # Should not have 'podiums' key
        assert "podiums" not in result


class TestNationalityParsing:
    """Tests for Nationality field parsing."""

    def test_nationality_multiple_with_or(self, cell_parser):
        """Test nationality with 'or' separator: American or Italian."""
        html = """<td class="infobox-data">American or Italian</td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_nationality(cell)

        assert result == ["American", "Italian"]

    def test_nationality_with_years(self, cell_parser):
        """Test nationality with year information."""
        html = """<td class="infobox-data">
            Federation of Rhodesia and Nyasaland (1963)<br>
            Rhodesian (1964) (1965, 1967–1968)<br>
            Rhodesian (1969)
        </td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_nationality(cell)

        assert isinstance(result, list)
        assert len(result) == 3

        # First entry: Federation of Rhodesia and Nyasaland in 1963
        assert result[0]["nationality"] == "Federation of Rhodesia and Nyasaland"
        assert result[0]["years"] == [1963]

        # Second entry: Rhodesian (1964) in 1964, 1965, 1967, 1968
        assert "Rhodesian" in result[1]["nationality"]
        assert 1964 in result[1]["years"]
        assert 1965 in result[1]["years"]
        assert 1967 in result[1]["years"]
        assert 1968 in result[1]["years"]

        # Third entry: Rhodesian in 1969
        assert "Rhodesian" in result[2]["nationality"]
        assert result[2]["years"] == [1969]


class TestMajorVictoriesParsing:
    """Tests for Major victories parsing."""

    def test_major_victories_from_full_data(self, titles_parser):
        """Test parsing major victories from full_data cell."""
        html = """<td colspan="2" class="infobox-full-data">
            <b>Major victories</b> <br>
            <a href="/wiki/24_Hours_of_Le_Mans" title="24 Hours of Le Mans">24 Hours of Le Mans</a>
            (<a href="/wiki/1934_24_Hours_of_Le_Mans" title="1934 24 Hours of Le Mans">1934</a>)
        </td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = titles_parser.parse_major_victories_from_full_data(cell)

        assert len(result) == 1
        assert result[0]["title"]["text"] == "24 Hours of Le Mans"
        assert len(result[0]["years"]) == 1
        assert result[0]["years"][0]["text"] == "1934"


class TestFullDataRacesRun:
    """Tests for races run parsing from full data."""

    def test_races_run_pattern(self, cell_parser):
        """Test parsing '97 races run over 6 years' pattern."""
        html = """<td colspan="2" class="infobox-full-data">97 races run over 6 years</td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_full_data(cell)

        assert result["races_run"] == 97

    def test_full_data_with_null_text(self, cell_parser):
        """Test that parse_full_data handles None text gracefully."""
        html = """<td colspan="2" class="infobox-full-data"></td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        # Should not raise an error
        result = cell_parser.parse_full_data(cell)

        assert "text" in result
