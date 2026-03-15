from bs4 import BeautifulSoup

from scrapers.wiki.parsers.content_text import ContentTextParser


def _parse_content(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    return ContentTextParser().parse(soup.find("div"))


def _collect_leaf_elements(items: list[dict]) -> list[dict]:
    leaf: list[dict] = []
    for section_l2 in items:
        for section_l3 in section_l2["data"]["items"]:
            for section_l4 in section_l3["data"]["items"]:
                for section_l5 in section_l4["data"]["items"]:
                    leaf.extend(section_l5["data"]["items"])
    return leaf


def test_wiki_section_result_has_unified_contract() -> None:
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <div class="mw-heading mw-heading2"><h2 id="Career">Career</h2></div>
      <div class="mw-heading mw-heading3"><h3 id="As_driver">As driver</h3></div>
      <div class="mw-heading mw-heading4"><h4 id="Highlights">Highlights</h4></div>
      <div class="mw-heading mw-heading5"><h5 id="Stats">Stats</h5></div>
      <p>Some text</p>
      <ul><li>One</li><li>Two</li></ul>
      <table class="wikitable"><tr><th>Year</th></tr><tr><td>2020</td></tr></table>
      <figure><img src="test.png"/><figcaption>Image</figcaption></figure>
    </div>
    """
    result = _parse_content(html)

    assert "items" in result
    leaf_elements = _collect_leaf_elements(result["items"])
    assert {item["type"] for item in leaf_elements} == {"paragraph", "list", "table", "figure"}

    for item in leaf_elements:
        assert set(item) == {"type", "meta", "data"}
        assert set(item["meta"]) >= {"section_id", "heading_id", "heading_path", "position"}
        assert item["meta"]["heading_path"][-1] == item["meta"]["section_id"]


def test_wiki_section_result_keeps_legacy_adapter() -> None:
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <p>Intro</p>
    </div>
    """
    result = _parse_content(html)

    assert "sections" in result
    assert result["sections"][0]["name"] == "(Top)"
    elements = result["sections"][0]["sub_sections"][0]["sub_sub_sections"][0]["sub_sub_sub_sections"][0]["elements"]
    assert elements[0]["type"] == "paragraph"
    assert "meta" not in elements[0]
