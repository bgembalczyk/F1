from bs4 import BeautifulSoup

from scrapers.wiki.parsers.content_text import ContentTextParser


def _parse_sections(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    parsed = ContentTextParser().parse(soup.find("div", id="mw-content-text"))
    return parsed["sections"]


def _snapshot_payload(sections: list[dict]) -> list[dict]:
    payload = []
    for section in sections:
        payload.append(
            {
                "name": section["name"],
                "section_id": section["section_id"],
                "kinds": [
                    el["kind"]
                    for sub in section.get("sub_sections", [])
                    for s2 in sub.get("sub_sub_sections", [])
                    for s3 in s2.get("sub_sub_sub_sections", [])
                    for el in s3.get("elements", [])
                ],
            }
        )
    return payload


def test_snapshot_driver_page_sections() -> None:
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <p>Intro</p>
      <div class="mw-heading mw-heading2"><h2 id="Career">Career</h2></div>
      <div class="mw-heading mw-heading3"><h3 id="Formula_One">Formula One</h3></div>
      <div><span><p>Debut in 2007.</p></span></div>
    </div>
    """
    snapshot = _snapshot_payload(_parse_sections(html))
    assert snapshot[1]["section_id"] == "career"
    assert "paragraph" in snapshot[1]["kinds"]


def test_snapshot_constructor_page_sections() -> None:
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <div class="mw-heading mw-heading2"><h2 id="Results">Results</h2></div>
      <div class="mw-heading mw-heading3"><h3 id="Championship_results">Championship results</h3></div>
      <div><table class="wikitable"><tr><th>Year</th></tr><tr><td>2024</td></tr></table></div>
    </div>
    """
    snapshot = _snapshot_payload(_parse_sections(html))
    assert snapshot[1]["section_id"] == "results"
    assert "table" in snapshot[1]["kinds"]


def test_snapshot_gp_page_sections() -> None:
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <div class="mw-heading mw-heading2"><h2 id="Race">Race</h2></div>
      <div class="mw-heading mw-heading3"><h3 id="Classification">Classification</h3></div>
      <span><ul><li>P1</li></ul></span>
    </div>
    """
    snapshot = _snapshot_payload(_parse_sections(html))
    assert snapshot[1]["section_id"] == "race"
    assert "list" in snapshot[1]["kinds"]


def test_snapshot_season_page_sections() -> None:
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <div class="mw-heading mw-heading2"><h2 id="Grands_Prix">Grands Prix</h2></div>
      <div class="mw-heading mw-heading3"><h3 id="Rounds">Rounds</h3></div>
      <p>24 races.</p>
    </div>
    """
    snapshot = _snapshot_payload(_parse_sections(html))
    assert snapshot[1]["section_id"] == "grands_prix"
    assert "paragraph" in snapshot[1]["kinds"]


def test_snapshot_circuit_page_sections() -> None:
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <div class="mw-heading mw-heading2"><h2 id="Layout">Layout</h2></div>
      <div class="mw-heading mw-heading3"><h3 id="Current">Current</h3></div>
      <figure><img src="x.png"/></figure>
    </div>
    """
    snapshot = _snapshot_payload(_parse_sections(html))
    assert snapshot[1]["section_id"] == "layout"
    assert "figure" in snapshot[1]["kinds"]
