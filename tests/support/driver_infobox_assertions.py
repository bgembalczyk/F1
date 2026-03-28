from __future__ import annotations

from bs4 import BeautifulSoup

EXPECTED_RECORDS_COUNT = 2
FIRST_NUMBER = 27
FIRST_START_YEAR = 2014
FIRST_END_YEAR = 2015
SECOND_NUMBER = 25
SECOND_START_YEAR = 2015


def assert_car_number_with_present(cell_parser) -> None:
    html = (
        '<td class="infobox-data">'
        '27 (<a href="/wiki/2014-15_Formula_E_Championship" '
        'title="2014-15 Formula E Championship">2014-2015</a>)<br>'
        '25 (<a href="/wiki/2015-16_Formula_E_Championship" '
        'title="2015-16 Formula E Championship">2015</a>-present)'
        "</td>"
    )
    cell = BeautifulSoup(html, "html.parser").find("td")
    result = cell_parser.parse_car_numbers(cell)

    assert len(result) == EXPECTED_RECORDS_COUNT
    assert result[0]["number"] == FIRST_NUMBER
    assert result[0]["years"]["start"] == FIRST_START_YEAR
    assert result[0]["years"]["end"] == FIRST_END_YEAR

    assert result[1]["number"] == SECOND_NUMBER
    assert result[1]["years"]["start"] == SECOND_START_YEAR
    assert result[1]["years"]["end"] is None
