from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.table.parser import HtmlTableParser


def test_html_table_parser_skips_repeated_header_rows() -> None:
    html = """
    <html>
      <body>
        <table class="wikitable">
          <tr>
            <th>Driver</th>
            <th>Season</th>
          </tr>
          <tr>
            <td>Juan Manuel Fangio</td>
            <td>1951</td>
          </tr>
          <tr>
            <th>Driver</th>
            <th>Season</th>
          </tr>
        </table>
      </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")
    parser = HtmlTableParser(expected_headers=["Driver", "Season"])

    rows = parser.parse(soup)

    assert len(rows) == 1
    assert [cell.get_text(strip=True) for cell in rows[0].values()] == [
        "Juan Manuel Fangio",
        "1951",
    ]
