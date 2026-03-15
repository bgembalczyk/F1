# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
"""Tests for driver infobox parser fixes."""

import pytest
from bs4 import BeautifulSoup

from scrapers.drivers.infobox.parsers.cell import InfoboxCellParser
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


@pytest.fixture()
def link_extractor():
    return InfoboxLinkExtractor(
        include_urls=True,
        wikipedia_base="https://en.wikipedia.org",
    )


@pytest.fixture()
def cell_parser(link_extractor):
    return InfoboxCellParser(include_urls=True, link_extractor=link_extractor)


class TestBestFinishWithClass:
    """Tests for best finish parsing with class information."""

    def test_single_season_with_class(self, cell_parser):
        """Test best finish with single season and class in parentheses."""
        html = """<td class="infobox-data">1st in <a href="/wiki/2014_FIA_World_Endurance_Championship" title="2014 FIA World Endurance Championship">2014</a> <small>(<a href="/wiki/Le_Mans_Prototype" title="Le Mans Prototype">LMP1</a>)</small></td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_best_finish(cell)

        assert result["result"] == "1st"
        assert len(result["seasons"]) == 1
        assert result["seasons"][0]["text"] == "2014"
        assert (
            result["seasons"][0]["url"]
            == "https://en.wikipedia.org/wiki/2014_FIA_World_Endurance_Championship"
        )
        assert "class" in result["seasons"][0]
        assert result["seasons"][0]["class"]["text"] == "LMP1"
        assert (
            result["seasons"][0]["class"]["url"]
            == "https://en.wikipedia.org/wiki/Le_Mans_Prototype"
        )

    def test_multiple_seasons_with_single_class(self, cell_parser):
        """Test best finish with multiple seasons sharing one class."""
        html = """<td class="infobox-data">1st in <a href="/wiki/2021_European_Le_Mans_Series" title="2021 European Le Mans Series">2021</a>, <a href="/wiki/2024_European_Le_Mans_Series" title="2024 European Le Mans Series">2024</a> <small>(<a href="/wiki/LMP2" class="mw-redirect" title="LMP2">LMP2</a>)</small></td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_best_finish(cell)

        assert result["result"] == "1st"
        assert len(result["seasons"]) == 2

        # Both seasons should have the same class
        for i, year in enumerate(["2021", "2024"]):
            assert result["seasons"][i]["text"] == year
            assert "class" in result["seasons"][i]
            assert result["seasons"][i]["class"]["text"] == "LMP2"
            assert (
                result["seasons"][i]["class"]["url"]
                == "https://en.wikipedia.org/wiki/LMP2"
            )

    def test_multiple_seasons_each_with_different_class(self, cell_parser):
        """Test best finish with different class for each season."""
        html = """<td class="infobox-data">1st in <a href="/wiki/2019%E2%80%9320_FIA_World_Endurance_Championship" title="2019–20 FIA World Endurance Championship">2019–20</a><span class="nowrap">&nbsp;</span><small>(<a href="/wiki/Le_Mans_Prototype" title="Le Mans Prototype">LMP1</a>)</small>, <a href="/wiki/2021_FIA_World_Endurance_Championship" title="2021 FIA World Endurance Championship">2021</a><span class="nowrap">&nbsp;</span><small>(<a href="/wiki/Le_Mans_Hypercar" title="Le Mans Hypercar">LMH</a>)</small></td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_best_finish(cell)

        assert result["result"] == "1st"
        assert len(result["seasons"]) == 2

        # First season with LMP1
        assert result["seasons"][0]["text"] == "2019-20"
        assert "class" in result["seasons"][0]
        assert result["seasons"][0]["class"]["text"] == "LMP1"

        # Second season with LMH
        assert result["seasons"][1]["text"] == "2021"
        assert "class" in result["seasons"][1]
        assert result["seasons"][1]["class"]["text"] == "LMH"

    def test_best_finish_without_class(self, cell_parser):
        """Test best finish without class information still works."""
        html = """<td class="infobox-data">6th (<a href="/wiki/2021_IndyCar_Series" title="2021 IndyCar Series">2021</a>, <a href="/wiki/2022_IndyCar_Series" title="2022 IndyCar Series">2022</a>)</td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_best_finish(cell)

        assert result["result"] == "6th"
        assert len(result["seasons"]) == 2
        # Should not have class field when not present
        assert "class" not in result["seasons"][0]
        assert "class" not in result["seasons"][1]

    def test_best_finish_season_in_small_tag_not_treated_as_class(self, cell_parser):
        """Test that season link in small tag is not incorrectly treated as class."""
        # Issue: When season is inside <small> tag without a real class,
        # it was being duplicated as a class field
        html = """<td class="infobox-data">2nd <small>(<a href="/wiki/2013_24_Hours_of_Le_Mans" title="2013 24 Hours of Le Mans">2013</a>)</small></td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_best_finish(cell)

        assert result["result"] == "2nd"
        assert len(result["seasons"]) == 1
        assert result["seasons"][0]["text"] == "2013"
        assert (
            result["seasons"][0]["url"]
            == "https://en.wikipedia.org/wiki/2013_24_Hours_of_Le_Mans"
        )
        # Should NOT have class field because "2013" is a year, not a class
        assert "class" not in result["seasons"][0]

    def test_best_finish_with_year_range_in_small_not_treated_as_class(
        self,
        cell_parser,
    ):
        """Test that year range in small tag is not treated as class."""
        html = """<td class="infobox-data">1st <small>(<a href="/wiki/2014_Le_Mans" title="2014 Le Mans">2014</a>, <a href="/wiki/2015_Le_Mans" title="2015 Le Mans">2015</a>)</small></td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_best_finish(cell)

        assert result["result"] == "1st"
        assert len(result["seasons"]) == 2
        # Neither season should have a class field
        assert "class" not in result["seasons"][0]
        assert "class" not in result["seasons"][1]


class TestRacingLicenceWithYears:
    """Tests for racing licence parsing with year ranges."""

    def test_licence_with_until_year(self, cell_parser):
        """Test licence with 'until YYYY' format."""
        html = """<td class="infobox-data">
            <a href="/wiki/FIA_Gold_Categorisation" title="FIA Gold Categorisation">FIA Gold</a>
            <span style="font-size: 85%;">(until 2019)</span>
        </td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_racing_licence(cell)

        assert len(result) == 1
        assert result[0]["licence"]["text"] == "FIA Gold"
        assert result[0]["years"]["start"] is None
        assert result[0]["years"]["end"] == 2019

    def test_licence_with_start_year_dash(self, cell_parser):
        """Test licence with 'YYYY–' format (open-ended)."""
        html = """<td class="infobox-data">
            <a href="/wiki/FIA_Platinum_Categorisation" title="FIA Platinum Categorisation">FIA Platinum</a>
            <span style="font-size: 85%;">(2020–)</span>
        </td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_racing_licence(cell)

        assert len(result) == 1
        assert result[0]["licence"]["text"] == "FIA Platinum"
        assert result[0]["years"]["start"] == 2020
        assert result[0]["years"]["end"] is None

    def test_multiple_licences_with_years(self, cell_parser):
        """Test multiple licences with different year ranges."""
        html = """<td class="infobox-data">
            <span typeof="mw:File"><a href="/wiki/File:FIA_Gold_Driver.png" class="mw-file-description"><img src="//upload.wikimedia.org/wikipedia/commons/thumb/e/e0/FIA_Gold_Driver.png/20px-FIA_Gold_Driver.png" decoding="async" width="12" height="12" class="mw-file-element"></a></span>
            <a href="/wiki/FIA_Gold_Categorisation" title="FIA Gold Categorisation">FIA Gold</a>
            <span style="font-size: 85%;">(until 2019)</span><br>
            <span typeof="mw:File"><a href="/wiki/File:FIA_Platinum_Driver.png" class="mw-file-description"><img src="//upload.wikimedia.org/wikipedia/commons/thumb/1/17/FIA_Platinum_Driver.png/20px-FIA_Platinum_Driver.png" decoding="async" width="12" height="12" class="mw-file-element"></a></span>
            <a href="/wiki/FIA_Platinum_Categorisation" title="FIA Platinum Categorisation">FIA Platinum</a>
            <span style="font-size: 85%;">(2020–)</span>
        </td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_racing_licence(cell)

        assert len(result) == 2

        # First licence: FIA Gold until 2019
        assert result[0]["licence"]["text"] == "FIA Gold"
        assert result[0]["years"]["start"] is None
        assert result[0]["years"]["end"] == 2019

        # Second licence: FIA Platinum from 2020
        assert result[1]["licence"]["text"] == "FIA Platinum"
        assert result[1]["years"]["start"] == 2020
        assert result[1]["years"]["end"] is None

    def test_licence_with_full_year_range(self, cell_parser):
        """Test licence with full year range 'YYYY-YYYY'."""
        html = """<td class="infobox-data">
            <a href="/wiki/FIA_Silver_Categorisation" title="FIA Silver Categorisation">FIA Silver</a>
            <span style="font-size: 85%;">(2015-2018)</span>
        </td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_racing_licence(cell)

        assert len(result) == 1
        assert result[0]["licence"]["text"] == "FIA Silver"
        assert result[0]["years"]["start"] == 2015
        assert result[0]["years"]["end"] == 2018


class TestCarNumberWithPresent:
    """Tests for car number parsing with 'present' keyword."""

    def test_car_number_with_present(self, cell_parser):
        """Test that car number parsing handles 'present' as null end year."""
        html = """<td class="infobox-data">
            27 (<a href="/wiki/2014%E2%80%9315_Formula_E_Championship" title="2014–15 Formula E Championship">2014–2015</a>)<br>
            25 (<a href="/wiki/2015%E2%80%9316_Formula_E_Championship" title="2015–16 Formula E Championship">2015</a>–present)
        </td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_car_numbers(cell)

        assert len(result) == 2
        assert result[0]["number"] == 27
        assert result[0]["years"]["start"] == 2014
        assert result[0]["years"]["end"] == 2015

        assert result[1]["number"] == 25
        assert result[1]["years"]["start"] == 2015
        assert result[1]["years"]["end"] is None  # 'present' should be None


class TestBestFinishWithNavigableString:
    """Tests for best finish parsing with NavigableString between elements."""

    def test_best_finish_with_text_between_link_and_class(self, cell_parser):
        """Test that best finish handles NavigableString (text nodes) between season link and class."""
        # This HTML has text between the season link and a span containing small tag
        # The NavigableString followed by a span with small will trigger the bug
        html = """<td class="infobox-data">1st in <a href="/wiki/2009_Formula_E" title="2009 Formula E">2009</a>
text here <span><small>(<a href="/wiki/LMP1" title="LMP1">LMP1</a>)</small></span></td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        # This should not raise AttributeError: 'NavigableString' object has no attribute 'find_all'
        result = cell_parser.parse_best_finish(cell)

        assert result["result"] == "1st"
        assert len(result["seasons"]) == 1
        assert result["seasons"][0]["text"] == "2009"
        # Should find the class even with text in between
        assert "class" in result["seasons"][0]
        assert result["seasons"][0]["class"]["text"] == "LMP1"

    def test_best_finish_with_multiple_seasons_and_text_nodes(self, cell_parser):
        """Test best finish with multiple seasons and text nodes between elements."""
        html = """<td class="infobox-data">1st in <a href="/wiki/2019_WEC" title="2019 WEC">2019</a>
some text <span><small>(<a href="/wiki/LMP1" title="LMP1">LMP1</a>)</small></span>, <a href="/wiki/2021_WEC" title="2021 WEC">2021</a>
more text <span><small>(<a href="/wiki/LMH" title="LMH">LMH</a>)</small></span></td>"""

        cell = BeautifulSoup(html, "html.parser").find("td")
        result = cell_parser.parse_best_finish(cell)

        assert result["result"] == "1st"
        assert len(result["seasons"]) == 2

        # First season
        assert result["seasons"][0]["text"] == "2019"
        assert "class" in result["seasons"][0]
        assert result["seasons"][0]["class"]["text"] == "LMP1"

        # Second season
        assert result["seasons"][1]["text"] == "2021"
        assert "class" in result["seasons"][1]
        assert result["seasons"][1]["class"]["text"] == "LMH"
