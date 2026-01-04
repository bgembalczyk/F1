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
        wikipedia_base="https://en.wikipedia.org"
    )


@pytest.fixture
def cell_parser(link_extractor):
    return InfoboxCellParser(
        include_urls=True,
        link_extractor=link_extractor
    )


@pytest.fixture
def general_parser(link_extractor):
    return InfoboxGeneralParser(
        include_urls=True,
        link_extractor=link_extractor,
        schema=DRIVER_GENERAL_SCHEMA,
        logger=None
    )


@pytest.fixture
def titles_parser(link_extractor):
    return InfoboxTitlesParser(link_extractor)


def test_birthplace_parsing_with_div(general_parser):
    """Test that birthplace is correctly extracted from div.birthplace element."""
    html = '''
    <td class="infobox-data">
        <span style="display:none">(<span class="bday">1985-12-27</span>)</span>
        27 December 1985<span class="noprint ForceAgeToShow"> (age&nbsp;40)</span><br>
        <div style="display:inline" class="birthplace">
            <a href="/wiki/Etterbeek" title="Etterbeek">Etterbeek</a>, Brussels, Belgium
        </div>
    </td>
    '''
    cell = BeautifulSoup(html, 'html.parser').find('td')
    result = general_parser._parse_date_place(cell)
    
    assert result['date'] == '1985-12-27'
    assert result['place'] is not None
    assert len(result['place']) == 3
    assert result['place'][0]['text'] == 'Etterbeek'
    assert result['place'][0]['url'] == 'https://en.wikipedia.org/wiki/Etterbeek'
    assert result['place'][1] == 'Brussels'
    assert result['place'][2] == 'Belgium'


def test_empty_flag_links_filtered(link_extractor):
    """Test that empty flag links are filtered out."""
    html = '''
    <td>
        <a href="/wiki/Germany" title="Germany"></a>
        <a href="/wiki/German_people" title="German">German</a>
    </td>
    '''
    cell = BeautifulSoup(html, 'html.parser').find('td')
    links = link_extractor.extract_links(cell)
    
    # Should only have the link with text
    assert len(links) == 1
    assert links[0]['text'] == 'German'


def test_best_finish_multiple_seasons(cell_parser):
    """Test that best finish extracts multiple seasons as a list."""
    html = '''
    <td class="infobox-data">
        6th (<a href="/wiki/2021_IndyCar_Series" title="2021 IndyCar Series">2021</a>, 
        <a href="/wiki/2022_IndyCar_Series" title="2022 IndyCar Series">2022</a>, 
        <a href="/wiki/2023_IndyCar_Series" title="2023 IndyCar Series">2023</a>)
    </td>
    '''
    cell = BeautifulSoup(html, 'html.parser').find('td')
    result = cell_parser.parse_best_finish(cell)
    
    assert result['result'] == '6th'
    assert result['seasons'] is not None
    assert len(result['seasons']) == 3
    assert result['seasons'][0]['text'] == '2021'
    assert result['seasons'][1]['text'] == '2022'
    assert result['seasons'][2]['text'] == '2023'


def test_race_event_parsing(cell_parser):
    """Test that race events are parsed into season, race, and circuit."""
    html = '''
    <td class="infobox-data">
        <a href="/wiki/2019_IndyCar_Series" title="2019 IndyCar Series">2019</a> 
        <a href="/wiki/2019_Firestone_Grand_Prix_of_St._Petersburg" title="2019 Firestone Grand Prix of St. Petersburg">Grand Prix of St. Petersburg</a> 
        (<a href="/wiki/Grand_Prix_of_St._Petersburg" title="Grand Prix of St. Petersburg">St. Petersburg</a>)
    </td>
    '''
    cell = BeautifulSoup(html, 'html.parser').find('td')
    result = cell_parser.parse_race_event(cell)
    
    assert result['season'] is not None
    assert result['season']['text'] == '2019'
    assert result['race'] is not None
    assert result['race']['text'] == 'Grand Prix of St. Petersburg'
    assert result['circuit'] is not None
    assert result['circuit']['text'] == 'St. Petersburg'


def test_stats_table_extraction(cell_parser):
    """Test extraction of Wins, Podiums, Poles from embedded table."""
    html = '''
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
    '''
    cell = BeautifulSoup(html, 'html.parser').find('td')
    result = cell_parser.parse_full_data(cell)
    
    assert 'wins' in result
    assert 'podiums' in result
    assert 'poles' in result
    assert result['wins'] == 4
    assert result['podiums'] == 11
    assert result['poles'] == 0


def test_class_wins_parsing(cell_parser):
    """Test that class wins are parsed like championships."""
    html = '''
    <td class="infobox-data">
        6 <small>
            (<a href="/wiki/1969_24_Hours_of_Le_Mans" title="1969 24 Hours of Le Mans">1969</a>, 
            <a href="/wiki/1975_24_Hours_of_Le_Mans" title="1975 24 Hours of Le Mans">1975</a>, 
            <a href="/wiki/1976_24_Hours_of_Le_Mans" title="1976 24 Hours of Le Mans">1976</a>)
        </small>
    </td>
    '''
    cell = BeautifulSoup(html, 'html.parser').find('td')
    result = cell_parser.parse_class_wins(cell)
    
    assert result['count'] == 6
    assert len(result['wins']) == 3
    assert result['wins'][0]['year'] == 1969
    assert result['wins'][1]['year'] == 1975
    assert result['wins'][2]['year'] == 1976


def test_previous_series_list_items(titles_parser):
    """Test that previous series correctly matches series to year ranges using list items."""
    html_label = '''
    <th class="infobox-label">
        <div class="plainlist">
            <ul>
                <li><a href="/wiki/2021_Formula_2_Championship">2021</a>–<a href="/wiki/2023_Formula_2_Championship">2023</a></li>
                <li><a href="/wiki/2020_FIA_Formula_3_Championship">2020</a>–<a href="/wiki/2021_FIA_Formula_3_Championship">2021</a></li>
            </ul>
        </div>
    </th>
    '''
    html_value = '''
    <td class="infobox-data">
        <div class="plainlist">
            <ul>
                <li><a href="/wiki/FIA_Formula_2" title="FIA Formula 2">FIA Formula 2</a></li>
                <li><a href="/wiki/FIA_Formula_3" title="FIA Formula 3">FIA Formula 3</a></li>
            </ul>
        </div>
    </td>
    '''
    label_cell = BeautifulSoup(html_label, 'html.parser').find('th')
    value_cell = BeautifulSoup(html_value, 'html.parser').find('td')
    
    rows = [{"label_cell": label_cell, "value_cell": value_cell}]
    result = titles_parser.parse_previous_series(rows)
    
    assert len(result) == 2
    assert result[0]['title']['text'] == 'FIA Formula 2'
    assert len(result[0]['years']) == 3  # 2021, 2022, 2023
    assert result[0]['years'][0]['year'] == 2021
    assert result[0]['years'][2]['year'] == 2023
    
    assert result[1]['title']['text'] == 'FIA Formula 3'
    assert len(result[1]['years']) == 2  # 2020, 2021
    assert result[1]['years'][0]['year'] == 2020
    assert result[1]['years'][1]['year'] == 2021
