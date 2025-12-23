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
    assert rows[0].headers == ["Driver", "Season"]
    assert [cell.get_text(strip=True) for cell in rows[0].cells] == [
        "Juan Manuel Fangio",
        "1951",
    ]
    assert rows[0].raw_tr.name == "tr"


def test_html_table_parser_uses_fragment_when_section_id_missing() -> None:
    html = """
    <html>
      <body>
        <h2><span id="Target">Target</span></h2>
        <table class="wikitable">
          <tr>
            <th>Name</th>
          </tr>
          <tr>
            <td>First</td>
          </tr>
        </table>
        <h2><span id="Other">Other</span></h2>
        <table class="wikitable">
          <tr>
            <th>Name</th>
          </tr>
          <tr>
            <td>Second</td>
          </tr>
        </table>
      </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")
    parser = HtmlTableParser(fragment="Target", expected_headers=["Name"])

    rows = parser.parse(soup)

    assert rows[0].headers == ["Name"]
    assert [cell.get_text(strip=True) for cell in rows[0].cells] == ["First"]
