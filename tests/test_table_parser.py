from bs4 import BeautifulSoup

from scrapers.base.table.parser import HtmlTableParser

EXPECTED_TABLE_COUNT = 2
EXPECTED_STANDINGS_COLUMNS = 7


def test_html_table_parser_skips_blank_header_separators() -> None:
    """Blank <th> cells used as visual separators in standings tables should be
    removed from the header list.  Wikipedia F1 standings tables split race columns
    into two groups with an empty <th> between them.  That blank header has no
    corresponding data cell in body rows, so including it shifts every subsequent
    column by one position.
    """
    html = """
    <html>
      <body>
        <table class="wikitable">
          <tr>
            <th>Pos</th>
            <th>Driver</th>
            <th><a href="/ARG">ARG</a></th>
            <th><a href="/BRA">BRA</a></th>
            <th><a href="/FRA">FRA</a></th>
            <th></th>
            <th><a href="/GBR">GBR</a></th>
            <th>Points</th>
          </tr>
          <tr>
            <td>1</td>
            <td>Alan Jones</td>
            <td>1</td>
            <td>3</td>
            <td>1</td>
            <td>1</td>
            <td>67</td>
          </tr>
        </table>
      </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")
    parser = HtmlTableParser(expected_headers=["Driver"])

    rows = parser.parse(soup)

    assert len(rows) == 1
    assert "" not in rows[0].headers, "Blank separator header should be dropped"
    assert len(rows[0].headers) == EXPECTED_STANDINGS_COLUMNS
    cell_texts = [c.get_text(strip=True) for c in rows[0].cells]
    header_map = dict(zip(rows[0].headers, cell_texts, strict=False))
    assert header_map["GBR"] == "1", f"GBR should map to 1, got {header_map['GBR']!r}"
    assert (
        header_map["Points"] == "67"
    ), f"Points should map to 67, got {header_map['Points']!r}"


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


def test_html_table_parser_skips_source_footer_row() -> None:
    html = """
    <html>
      <body>
        <table class="wikitable">
          <tr>
            <th>Year</th>
            <th>Driver</th>
          </tr>
          <tr>
            <td>1953</td>
            <td>Alberto Ascari</td>
          </tr>
          <tr>
            <th colspan="2">Source: Example</th>
          </tr>
        </table>
      </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")
    parser = HtmlTableParser(expected_headers=["Year", "Driver"])

    rows = parser.parse(soup)

    assert len(rows) == 1
    assert [cell.get_text(strip=True) for cell in rows[0].cells] == [
        "1953",
        "Alberto Ascari",
    ]


def test_html_table_parser_expands_rowspans() -> None:
    html = """
    <html>
      <body>
        <table class="wikitable">
          <tr>
            <th>Year</th>
            <th>Location</th>
            <th>Report</th>
          </tr>
          <tr>
            <td>1953</td>
            <td rowspan="2">Buenos Aires</td>
            <td>Report 1953</td>
          </tr>
          <tr>
            <td>1954</td>
            <td>Report 1954</td>
          </tr>
        </table>
      </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")
    parser = HtmlTableParser(expected_headers=["Year", "Location", "Report"])

    rows = parser.parse(soup)

    assert len(rows) == EXPECTED_TABLE_COUNT
    assert [cell.get_text(strip=True) for cell in rows[1].cells] == [
        "1954",
        "Buenos Aires",
        "Report 1954",
    ]
