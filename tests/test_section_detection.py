from bs4 import BeautifulSoup

from scrapers.base.helpers.html_utils import find_heading
from scrapers.wiki.parsers.section_detection import find_section_heading


def test_find_section_heading_prefers_exact_id_over_text() -> None:
    html = """
    <h2 id="Results"><span class="mw-headline">Overview</span></h2>
    <h2><span class="mw-headline">Results</span></h2>
    """
    soup = BeautifulSoup(html, "html.parser")

    match = find_section_heading(soup, "Results")

    assert match is not None
    assert match.strategy == "exact_id"
    assert match.heading.get("id") == "Results"


def test_find_section_heading_prefers_exact_text_over_fuzzy() -> None:
    html = """
    <h2><span class="mw-headline">Result</span></h2>
    <h2><span class="mw-headline">Results and standings</span></h2>
    """
    soup = BeautifulSoup(html, "html.parser")

    match = find_section_heading(soup, "Results")

    assert match is not None
    assert match.strategy == "exact_text"
    assert match.heading.get_text(" ", strip=True) == "Result"


def test_find_section_heading_supports_fuzzy_layout_variants() -> None:
    html = """
    <h2><span class="mw-headline">Career result</span></h2>
    """
    soup = BeautifulSoup(html, "html.parser")

    match = find_section_heading(soup, "Career results")

    assert match is not None
    assert match.strategy == "fuzzy"


def test_find_heading_uses_domain_aliases() -> None:
    html = """
    <h2><span class="mw-headline">Grands Prix</span></h2>
    """
    soup = BeautifulSoup(html, "html.parser")

    heading = find_heading(soup, "Results", domain="seasons")

    assert heading is not None
    assert heading.get_text(" ", strip=True) == "Grands Prix"
