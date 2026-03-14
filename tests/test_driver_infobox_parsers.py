"""Tests for driver infobox parsers."""

import pytest
from bs4 import BeautifulSoup

from scrapers.drivers.infobox.parsers.cell import InfoboxCellParser
from scrapers.drivers.infobox.parsers.general import InfoboxGeneralParser
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor
from scrapers.drivers.infobox.parsers.title import InfoboxTitlesParser
from scrapers.drivers.infobox.schema import DRIVER_GENERAL_SCHEMA


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
        schema=DRIVER_GENERAL_SCHEMA,
        logger=None,
    )


@pytest.fixture
def titles_parser(link_extractor):
    return InfoboxTitlesParser(link_extractor)


def test_birthplace_parsing_with_div(general_parser):
    """Test that birthplace is correctly extracted from div.birthplace element."""
    html = """
    <td class="infobox-data">
        <span style="display:none">(<span class="bday">1985-12-27</span>)</span>
        27 December 1985<span class="noprint ForceAgeToShow"> (age&nbsp;40)</span><br>
        <div style="display:inline" class="birthplace">
            <a href="/wiki/Etterbeek" title="Etterbeek">Etterbeek</a>, Brussels, Belgium
        </div>
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = general_parser._parse_date_place(cell)

    assert result["date"] == "1985-12-27"
    assert result["place"] is not None
    assert len(result["place"]) == 3
    assert result["place"][0]["text"] == "Etterbeek"
    assert result["place"][0]["url"] == "https://en.wikipedia.org/wiki/Etterbeek"
    assert result["place"][1] == "Brussels"
    assert result["place"][2] == "Belgium"


def test_empty_flag_links_filtered(link_extractor):
    """Test that empty flag links are filtered out."""
    html = """
    <td>
        <a href="/wiki/Germany" title="Germany"></a>
        <a href="/wiki/German_people" title="German">German</a>
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    links = link_extractor.extract_links(cell)

    # Should only have the link with text
    assert len(links) == 1
    assert links[0]["text"] == "German"


def test_best_finish_multiple_seasons(cell_parser):
    """Test that best finish extracts multiple seasons as a list."""
    html = """
    <td class="infobox-data">
        6th (<a href="/wiki/2021_IndyCar_Series" title="2021 IndyCar Series">2021</a>,
        <a href="/wiki/2022_IndyCar_Series" title="2022 IndyCar Series">2022</a>,
        <a href="/wiki/2023_IndyCar_Series" title="2023 IndyCar Series">2023</a>)
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_best_finish(cell)

    assert result["result"] == "6th"
    assert result["seasons"] is not None
    assert len(result["seasons"]) == 3
    assert result["seasons"][0]["text"] == "2021"
    assert result["seasons"][1]["text"] == "2022"
    assert result["seasons"][2]["text"] == "2023"


def test_race_event_parsing(cell_parser):
    """Test that race events are parsed as a list of links."""
    html = """
    <td class="infobox-data">
        <a href="/wiki/2019_IndyCar_Series" title="2019 IndyCar Series">2019</a>
        <a href="/wiki/2019_Firestone_Grand_Prix_of_St._Petersburg" title="2019 Firestone Grand Prix of St. Petersburg">Grand Prix of St. Petersburg</a>
        (<a href="/wiki/Grand_Prix_of_St._Petersburg" title="Grand Prix of St. Petersburg">St. Petersburg</a>)
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_race_event(cell)

    # Should return a list of all links
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0]["text"] == "2019"
    assert result[1]["text"] == "Grand Prix of St. Petersburg"
    assert result[2]["text"] == "St. Petersburg"


def test_stats_table_extraction(cell_parser):
    """Test extraction of Wins, Podiums, Poles from embedded table."""
    html = """
    <td colspan="2" class="infobox-full-data">
        <table style="width:100%;">
            <tbody>
                <tr>
                    <th>Wins</th>
                    <th>Podiums</th>
                    <th>Poles</th>
                </tr>
                <tr>
                    <td>4</td>
                    <td>11</td>
                    <td>0</td>
                </tr>
            </tbody>
        </table>
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_full_data(cell)

    # Should only have wins, podiums, poles - no text or links
    assert "wins" in result
    assert "podiums" in result
    assert "poles" in result
    assert result["wins"] == 4
    assert result["podiums"] == 11
    assert result["poles"] == 0
    assert "text" not in result
    assert "links" not in result


def test_class_wins_parsing(cell_parser):
    """Test that class wins are parsed like championships."""
    html = """
    <td class="infobox-data">
        6 <small>
            (<a href="/wiki/1969_24_Hours_of_Le_Mans" title="1969 24 Hours of Le Mans">1969</a>,
            <a href="/wiki/1975_24_Hours_of_Le_Mans" title="1975 24 Hours of Le Mans">1975</a>,
            <a href="/wiki/1976_24_Hours_of_Le_Mans" title="1976 24 Hours of Le Mans">1976</a>)
        </small>
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_class_wins(cell)

    assert result["count"] == 6
    assert len(result["wins"]) == 3
    assert result["wins"][0]["year"] == 1969
    assert result["wins"][1]["year"] == 1975
    assert result["wins"][2]["year"] == 1976


def test_previous_series_list_items(titles_parser):
    """Test that previous series correctly matches series to year ranges using list items."""
    html_label = """
    <th class="infobox-label">
        <div class="plainlist">
            <ul>
                <li><a href="/wiki/2021_Formula_2_Championship">2021</a>–<a href="/wiki/2023_Formula_2_Championship">2023</a></li>
                <li><a href="/wiki/2020_FIA_Formula_3_Championship">2020</a>–<a href="/wiki/2021_FIA_Formula_3_Championship">2021</a></li>
            </ul>
        </div>
    </th>
    """
    html_value = """
    <td class="infobox-data">
        <div class="plainlist">
            <ul>
                <li><a href="/wiki/FIA_Formula_2" title="FIA Formula 2">FIA Formula 2</a></li>
                <li><a href="/wiki/FIA_Formula_3" title="FIA Formula 3">FIA Formula 3</a></li>
            </ul>
        </div>
    </td>
    """
    label_cell = BeautifulSoup(html_label, "html.parser").find("th")
    value_cell = BeautifulSoup(html_value, "html.parser").find("td")

    rows = [{"label_cell": label_cell, "value_cell": value_cell}]
    result = titles_parser.parse_previous_series(rows)

    assert len(result) == 2
    assert result[0]["title"]["text"] == "FIA Formula 2"
    assert len(result[0]["years"]) == 3  # 2021, 2022, 2023
    assert result[0]["years"][0]["year"] == 2021
    assert result[0]["years"][2]["year"] == 2023

    assert result[1]["title"]["text"] == "FIA Formula 3"
    assert len(result[1]["years"]) == 2  # 2020, 2021
    assert result[1]["years"][0]["year"] == 2020
    assert result[1]["years"][1]["year"] == 2021


def test_year_range_in_single_link_not_expanded(link_extractor):
    """Test that year ranges within a single link are kept as-is, not expanded.

    This handles cases like MRF Challenge where "2018-2019" is a single season name,
    not a range of years to expand.
    """
    html = """
    <li><a href="/wiki/2018%E2%80%9319_MRF_Challenge_Formula_2000_Championship"
           title="2018–19 MRF Challenge Formula 2000 Championship">2018–2019</a></li>
    """
    cell = BeautifulSoup(html, "html.parser")
    result = link_extractor.extract_year_list_with_links(cell)

    # Should keep the range as-is in a single entry with "text" field
    assert len(result) == 1
    assert result[0]["text"] == "2018-2019"
    assert (
        result[0]["url"]
        == "https://en.wikipedia.org/wiki/2018%E2%80%9319_MRF_Challenge_Formula_2000_Championship"
    )

    # Should NOT have "year" field (which would indicate expansion)
    assert "year" not in result[0]


def test_year_range_with_separate_links_expanded(link_extractor):
    """Test that year ranges with separate start/end links are still expanded."""
    html = """
    <div>
        <a href="/wiki/2021_Formula_2_Championship">2021</a>–<a href="/wiki/2023_Formula_2_Championship">2023</a>
    </div>
    """
    cell = BeautifulSoup(html, "html.parser")
    result = link_extractor.extract_year_list_with_links(cell)

    # Should expand to individual years
    assert len(result) == 3
    assert result[0]["year"] == 2021
    assert result[1]["year"] == 2022
    assert result[2]["year"] == 2023

    # Should NOT have "text" field (which would indicate non-expansion)
    for entry in result:
        assert "text" not in entry


def test_races_run_extraction(cell_parser):
    """Test extraction of races_run from 'X races run over Y years' text."""
    html = '<td colspan="2" class="infobox-full-data">97 races run over 6 years</td>'
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_full_data(cell)

    assert result == {"races_run": 97}


def test_championships_simple_links(cell_parser):
    """Test that championships treats parentheses content as simple list of links."""
    html = """
    <td class="infobox-data">
        1 (<a href="/wiki/2021%E2%80%9322_Formula_E_World_Championship"
             title="2021–22 Formula E World Championship">2021–22</a>)
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_championships(cell)

    assert result["count"] == 1
    assert isinstance(result["championships"], list)
    assert len(result["championships"]) == 1
    assert result["championships"][0]["text"] == "2021-22"
    assert "url" in result["championships"][0]


def test_car_number_year_range_multiple_dashes(cell_parser):
    """Test car number parsing with multiple dashes (e.g., 2018-19–2022)."""
    html = """
    <td class="infobox-data">
        5 (<a href="/wiki/2018%E2%80%9319_Formula_E_Championship">2018-19</a>–<a href="/wiki/2021%E2%80%9322_Formula_E_World_Championship">2022</a>)
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_car_numbers(cell)

    assert len(result) == 1
    assert result[0]["number"] == 5
    assert result[0]["years"]["start"] == 2018
    assert result[0]["years"]["end"] == 2022


def test_best_finish_no_links_extracts_years(cell_parser):
    """Test that best finish extracts years from parentheses when no links present."""
    html = '<td class="infobox-data">DNF (1983)</td>'
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_best_finish(cell)

    assert result["result"] == "DNF"
    assert result["seasons"] == [1983]


def test_finished_last_season_parsing(cell_parser):
    """Test parsing of Finished last season into position and points."""
    html = '<td class="infobox-data">14th (62 pts)</td>'
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_finished_last_season(cell)

    assert result["position"] == "14th"
    assert result["points"] == 62


def test_race_event_no_links(cell_parser):
    """Test race event parsing when no links present - should return text."""
    html = '<td class="infobox-data">1985 Provimi Veal 200 (Road America)</td>'
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_race_event(cell)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["text"] == "1985 Provimi Veal 200 (Road America)"
    assert result[0]["url"] is None


def test_racing_licence_with_years(cell_parser):
    """Test racing licence parsing with year ranges."""
    html = """
    <td class="infobox-data">
        <a href="/wiki/FIA_Gold_Categorisation" title="FIA Gold Categorisation">FIA Gold</a>
        <span style="font-size: 85%;">(until 2019)</span><br>
        <a href="/wiki/FIA_Platinum_Categorisation" title="FIA Platinum Categorisation">FIA Platinum</a>
        <span style="font-size: 85%;">(2020–)</span>
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_racing_licence(cell)

    assert len(result) == 2
    assert result[0]["licence"]["text"] == "FIA Gold"
    assert result[0]["years"]["end"] == 2019
    assert result[0]["years"]["start"] is None

    assert result[1]["licence"]["text"] == "FIA Platinum"
    assert result[1]["years"]["start"] == 2020
    assert result[1]["years"]["end"] is None


def test_died_with_deathplace(general_parser):
    """Test that died date/place extraction uses deathplace class."""
    html = """
    <td class="infobox-data">
        11 July 2015<span style="display:none">(2015-07-11)</span> (aged&nbsp;80)<br>
        <span class="deathplace">
            <a href="/wiki/Johannesburg" title="Johannesburg">Johannesburg</a>, South Africa
        </span>
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = general_parser._parse_date_place(cell)

    assert result["date"] == "2015-07-11"
    assert len(result["place"]) == 2
    assert result["place"][0]["text"] == "Johannesburg"
    assert result["place"][1] == "South Africa"


def test_parse_full_data_with_empty_cell(cell_parser):
    """Test that parse_full_data handles empty cells without crashing."""
    html = '<td class="infobox-data"></td>'
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_full_data(cell)

    # Should return a dict with text=None and links
    assert isinstance(result, dict)
    assert result["text"] is None
    assert "links" in result


def test_parse_full_data_with_whitespace_only(cell_parser):
    """Test that parse_full_data handles whitespace-only cells."""
    html = '<td class="infobox-data">   \n\t   </td>'
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_full_data(cell)

    # Should return a dict with text=None (whitespace is cleaned to None)
    assert isinstance(result, dict)
    assert result["text"] is None
    assert "links" in result


def test_parse_racing_licence_with_beautiful_soup(cell_parser):
    """Test that parse_racing_licence correctly uses BeautifulSoup (no NameError).

    This test verifies that BeautifulSoup is imported and can be used without
    raising a NameError. The method may return an empty list due to other logic
    issues, but the key is that it doesn't crash with 'BeautifulSoup is not defined'.
    """
    html = """
    <td class="infobox-data">
        <a href="/wiki/FIA_Gold_Categorisation" title="FIA Gold Categorisation">FIA Gold</a>
        <span style="font-size: 85%;">(until 2019)</span><br>
        <a href="/wiki/FIA_Platinum_Categorisation" title="FIA Platinum Categorisation">FIA Platinum</a>
        <span style="font-size: 85%;">(2020–)</span>
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")

    # This should not raise NameError for BeautifulSoup
    # The important thing is that it executes without a NameError
    try:
        result = cell_parser.parse_racing_licence(cell)
        # Should return a list (even if empty due to other logic issues)
        assert isinstance(result, list)
    except NameError as e:
        if "BeautifulSoup" in str(e):
            pytest.fail(f"BeautifulSoup is not imported: {e}")
        raise


def test_car_number_with_present(cell_parser):
    """Test that car number parsing handles 'present' as null end year."""
    html = """
    <td class="infobox-data">
        27 (<a href="/wiki/2014%E2%80%9315_Formula_E_Championship" title="2014–15 Formula E Championship">2014–2015</a>)<br>
        25 (<a href="/wiki/2015%E2%80%9316_Formula_E_Championship" title="2015–16 Formula E Championship">2015</a>–present)
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_car_numbers(cell)

    assert len(result) == 2
    assert result[0]["number"] == 27
    assert result[0]["years"]["start"] == 2014
    assert result[0]["years"]["end"] == 2015

    assert result[1]["number"] == 25
    assert result[1]["years"]["start"] == 2015
    assert result[1]["years"]["end"] is None  # 'present' should be None


def test_died_with_hidden_iso_date(general_parser):
    """Test that died date extraction uses hidden ISO date span."""
    html = """
    <tr><th scope="row" class="infobox-label">Died</th><td class="infobox-data">10 September 1961<span style="display:none">(1961-09-10)</span> (aged&nbsp;33)<br><div style="display:inline" class="deathplace"><a href="/wiki/Monza" title="Monza">Monza</a>, Italy</div></td></tr>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = general_parser._parse_date_place(cell)

    assert result["date"] == "1961-09-10"
    assert len(result["place"]) == 2
    assert result["place"][0]["text"] == "Monza"
    assert result["place"][0]["url"] == "https://en.wikipedia.org/wiki/Monza"
    assert result["place"][1] == "Italy"


def test_died_with_deathplace_div(general_parser):
    """Test that died date/place extraction works with div.deathplace."""
    html = """
    <td class="infobox-data">May 2, 2021<span style="display:none">(2021-05-02)</span> (aged&nbsp;87)<br><div class="deathplace"><a href="/wiki/Albuquerque,_New_Mexico" title="Albuquerque, New Mexico">Albuquerque, New Mexico</a>, U.S.</div></td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = general_parser._parse_date_place(cell)

    assert result["date"] == "2021-05-02"
    # Place should be split by commas from the link and remaining text
    assert len(result["place"]) >= 2
    # First element should be the link
    assert result["place"][0]["text"] == "Albuquerque, New Mexico"
    assert (
        result["place"][0]["url"]
        == "https://en.wikipedia.org/wiki/Albuquerque,_New_Mexico"
    )


def test_best_finish_with_multiple_classes(cell_parser):
    """Test that best finish associates class with specific season."""
    html = """
    <td class="infobox-data">1st in <a href="/wiki/2019%E2%80%9320_FIA_World_Endurance_Championship" title="2019–20 FIA World Endurance Championship">2019–20</a><span class="nowrap">&nbsp;</span><small>(<a href="/wiki/Le_Mans_Prototype" title="Le Mans Prototype">LMP1</a>)</small>, <a href="/wiki/2021_FIA_World_Endurance_Championship" title="2021 FIA World Endurance Championship">2021</a><span class="nowrap">&nbsp;</span><small>(<a href="/wiki/Le_Mans_Hypercar" title="Le Mans Hypercar">LMH</a>)</small></td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_best_finish(cell)

    assert result["result"] == "1st"
    assert len(result["seasons"]) == 2

    # First season with LMP1 class
    assert result["seasons"][0]["text"] == "2019-20"
    assert (
        result["seasons"][0]["url"]
        == "https://en.wikipedia.org/wiki/2019%E2%80%9320_FIA_World_Endurance_Championship"
    )
    assert "class" in result["seasons"][0]
    assert result["seasons"][0]["class"]["text"] == "LMP1"
    assert (
        result["seasons"][0]["class"]["url"]
        == "https://en.wikipedia.org/wiki/Le_Mans_Prototype"
    )

    # Second season with LMH class
    assert result["seasons"][1]["text"] == "2021"
    assert (
        result["seasons"][1]["url"]
        == "https://en.wikipedia.org/wiki/2021_FIA_World_Endurance_Championship"
    )
    assert "class" in result["seasons"][1]
    assert result["seasons"][1]["class"]["text"] == "LMH"
    assert (
        result["seasons"][1]["class"]["url"]
        == "https://en.wikipedia.org/wiki/Le_Mans_Hypercar"
    )


def test_previous_series_with_year_urls(link_extractor, titles_parser):
    """Test that previous series extracts year URLs from header correctly."""
    html_label = """
    <th class="infobox-label">
        <a href="/wiki/2004_Formula_Renault_seasons#2004_Asian_Formula_Renault_Challenge_season" title="2004 Formula Renault seasons">2004</a>
    </th>
    """
    html_value = """
    <td class="infobox-data">
        <a href="/wiki/Asian_Formula_Renault_Challenge" class="mw-redirect" title="Asian Formula Renault Challenge">Asian Formula Renault</a>
    </td>
    """
    label_cell = BeautifulSoup(html_label, "html.parser").find("th")
    value_cell = BeautifulSoup(html_value, "html.parser").find("td")

    rows = [{"label_cell": label_cell, "value_cell": value_cell}]
    result = titles_parser.parse_previous_series(rows)

    assert len(result) == 1
    assert result[0]["title"]["text"] == "Asian Formula Renault"
    assert (
        result[0]["title"]["url"]
        == "https://en.wikipedia.org/wiki/Asian_Formula_Renault_Challenge"
    )

    # Year should have URL from header
    assert len(result[0]["years"]) == 1
    assert result[0]["years"][0]["year"] == 2004
    assert (
        result[0]["years"][0]["url"]
        == "https://en.wikipedia.org/wiki/2004_Formula_Renault_seasons#2004_Asian_Formula_Renault_Challenge_season"
    )


def test_racing_licence_with_images(cell_parser):
    """Test racing licence parsing with image tags before links."""
    html = """
    <td class="infobox-data"><span typeof="mw:File"><a href="/wiki/File:FIA_Platinum_Driver.png" class="mw-file-description"><img src="//upload.wikimedia.org/wikipedia/commons/thumb/1/17/FIA_Platinum_Driver.png/20px-FIA_Platinum_Driver.png" decoding="async" width="12" height="12" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/17/FIA_Platinum_Driver.png/40px-FIA_Platinum_Driver.png 2x" data-file-width="93" data-file-height="93"></a></span> <a href="/wiki/FIA_Platinum_Categorisation" title="FIA Platinum Categorisation">FIA Platinum</a></td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_racing_licence(cell)

    # Should extract the FIA Platinum link, ignoring the image link
    assert len(result) >= 1
    assert result[0]["licence"]["text"] == "FIA Platinum"
    assert (
        result[0]["licence"]["url"]
        == "https://en.wikipedia.org/wiki/FIA_Platinum_Categorisation"
    )
