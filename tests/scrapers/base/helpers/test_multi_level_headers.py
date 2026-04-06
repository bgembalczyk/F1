import pytest
from bs4 import BeautifulSoup

from scrapers.base.helpers.multi_level_headers import MultiLevelHeaderBuilder


def _table(html: str):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    assert table is not None
    return table


def test_build_headers_for_two_level_header_fixture() -> None:
    table = _table(
        """
        <table class="wikitable">
          <tr><th>Driver</th><th colspan="2">Results</th></tr>
          <tr><th>Wins</th><th>Podiums</th></tr>
          <tr><td>A</td><td>1</td><td>3</td></tr>
        </table>
        """,
    )

    headers, header_rows = MultiLevelHeaderBuilder.build_headers(table)

    assert header_rows == 2
    assert headers == ["Driver", "Results - Wins", "Results - Podiums"]


def test_build_headers_with_missing_second_row_cell_falls_back_to_parent_header() -> (
    None
):
    table = _table(
        """
        <table>
          <tr><th colspan="3">Points</th></tr>
          <tr><th>Race</th><th>Sprint</th></tr>
          <tr><td>10</td><td>2</td><td>0</td></tr>
        </table>
        """,
    )

    headers, _ = MultiLevelHeaderBuilder.build_headers(table)

    assert headers == ["Points - Race", "Points - Sprint", "Points"]


def test_build_headers_with_nonstandard_colspan_or_invalid_value() -> None:
    table = _table(
        """
        <table>
          <tr><th>Season</th><th colspan="x">Stats</th><th colspan="3">Team</th></tr>
          <tr><th>Wins</th><th>Name</th><th>Country</th><th>Base</th></tr>
          <tr><td>1950</td><td>2</td><td>Alpha</td><td>UK</td><td>Silverstone</td></tr>
        </table>
        """,
    )

    headers, _ = MultiLevelHeaderBuilder.build_headers(table)

    assert headers == [
        "Season",
        "Stats",
        "Team - Wins",
        "Team - Name",
        "Team - Country",
    ]


def test_build_headers_raises_when_no_header_rows_found() -> None:
    table = _table(
        """
        <table>
          <tr><td>A</td><td>B</td></tr>
        </table>
        """,
    )

    with pytest.raises(RuntimeError, match="Nie znaleziono nagłówków tabeli"):
        MultiLevelHeaderBuilder.build_headers(table)
