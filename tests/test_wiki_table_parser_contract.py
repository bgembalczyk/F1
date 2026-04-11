from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from scrapers.parser_table import HtmlTableParser
from scrapers.parsers.table.wiki.circuit_list import CircuitsListTableParser
from scrapers.parsers.table.wiki.mapped.lap_records import LapRecordsWikiTableParser
from scrapers.parsers.table.wiki.mapped.race_results import RaceResultsTableParser
from scrapers.parsers.table.wiki.mapped.standings import StandingsTableParser

CONTRACT_HTML = """
<table class="wikitable">
  <tr>
    <th>Pos</th>
    <th>Points</th>
    <th>Driver</th>
    <th>Round</th>
    <th>Winning driver</th>
    <th>Time</th>
    <th>Driver/Rider</th>
    <th>Circuit</th>
    <th>Type</th>
    <th>Location</th>
    <th>Country</th>
  </tr>
  <tr>
    <td>1</td>
    <td>25</td>
    <td>Max Verstappen</td>
    <td>1</td>
    <td>Max Verstappen</td>
    <td>1:27.097</td>
    <td>Lewis Hamilton</td>
    <td>Silverstone</td>
    <td>Road course</td>
    <td>Silverstone</td>
    <td>United Kingdom</td>
  </tr>
</table>
"""


@pytest.mark.parametrize(
    "parser",
    [
        StandingsTableParser(),
        RaceResultsTableParser(),
        LapRecordsWikiTableParser(),
        CircuitsListTableParser(),
    ],
)
def test_wiki_table_parsers_contract_keep_uniform_output_shape(parser) -> None:
    soup = BeautifulSoup(CONTRACT_HTML, "html.parser")
    table = soup.find("table")
    assert table is not None

    rows = HtmlTableParser().parse_table(table)
    headers = rows[0].headers
    table_data = {
        "headers": headers,
        "rows": [
            dict(
                zip(
                    headers,
                    [cell.get_text(" ", strip=True) for cell in row.cells],
                    strict=False,
                ),
            )
            for row in rows
        ],
    }
    parsed = parser.parse(table_data)

    assert parsed is not None
    assert set(parsed.keys()) == {
        "table_type",
        "domain_column_map",
        "missing_columns_policy",
        "extra_columns_policy",
        "domain_rows",
    }
    assert isinstance(parsed["domain_column_map"], dict)
    assert isinstance(parsed["domain_rows"], list)
    assert len(parsed["domain_rows"]) == 1
    assert isinstance(parsed["domain_rows"][0], dict)
