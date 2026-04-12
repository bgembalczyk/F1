from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from scrapers.parsers.table.html_table import HtmlTableParser
from scrapers.parsers.wiki.circuit_list_table_mapper import CircuitsListTableMapper
from scrapers.parsers.lap_records_wiki_table_mapper import LapRecordsWikiTableMapper
from scrapers.parsers.race_results_table_mapper import RaceResultsTableMapper
from scrapers.parsers.standings_table_mapper import StandingsTableMapper

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
    "mapper",
    [
        StandingsTableMapper(),
        RaceResultsTableMapper(),
        LapRecordsWikiTableMapper(),
        CircuitsListTableMapper(),
    ],
)
def test_wiki_table_parsers_contract_keep_uniform_output_shape(mapper) -> None:
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
    parsed = mapper.map(table_data)

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
