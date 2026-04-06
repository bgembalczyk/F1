from bs4 import BeautifulSoup

from scrapers.drivers.infobox.parsers.collapsible_table import CollapsibleTableParser


class _Delegate:
    @staticmethod
    def parse_active_years(_cell):
        return [1960, 1961]

    @staticmethod
    def parse_teams(_cell):
        return [{"text": "Ferrari"}]

    @staticmethod
    def parse_race_event(cell):
        return {"text": cell.get_text(" ", strip=True)}

    @staticmethod
    def parse_cell(cell):
        return cell.get_text(" ", strip=True)


def _parse_table(html: str):
    table = BeautifulSoup(html, "html.parser").find("table")
    return CollapsibleTableParser(_Delegate()).parse_collapsible_career_table(table)


def test_collapsible_table_parser_parses_label_rows_and_numeric_values() -> None:
    result = _parse_table(
        """
        <table class="mw-collapsible">
          <tr><th>Motorcycle career</th></tr>
          <tr><th>Active years</th><td>1960-1961</td></tr>
          <tr><th>Team</th><td>Ferrari</td></tr>
          <tr><th>Starts</th><td>129</td></tr>
          <tr><th>First race</th><td>1960 Dutch TT</td></tr>
        </table>
        """,
    )

    assert result is not None
    assert result["title"] == "Motorcycle career"
    assert result["rows"][0]["value"] == [1960, 1961]
    assert result["rows"][1]["value"] == [{"text": "Ferrari"}]
    assert result["rows"][2]["value"] == 129  # noqa: PLR2004


def test_collapsible_table_parser_parses_nested_table_and_returns_none_for_empty(
) -> None:
    with_nested = _parse_table(
        """
        <table class="mw-collapsible">
          <tr><th>Stats</th></tr>
          <tr>
            <td colspan="2">
              <table>
                <tr><th>Wins</th><td>4</td></tr>
              </table>
            </td>
          </tr>
        </table>
        """,
    )

    assert with_nested is not None
    assert with_nested["rows"][0] == {"label": "Wins", "value": 4}

    empty = _parse_table(
        "<table class='mw-collapsible'><tr><th>Only title</th></tr></table>",
    )
    assert empty is None
