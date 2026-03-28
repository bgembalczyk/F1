from __future__ import annotations

from bs4 import BeautifulSoup


def assert_car_number_with_present(cell_parser) -> None:
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
    assert result[1]["years"]["end"] is None
