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


def test_find_section_heading_regression_multilevel_fixture() -> None:
    html = """
    <div class="mw-heading mw-heading2"><h2 id="History"><span class="mw-headline">History</span></h2></div>
    <div class="mw-heading mw-heading3"><h3 id="Origins"><span class="mw-headline">Origins</span></h3></div>
    <div class="mw-heading mw-heading2"><h2 id="Grands_Prix"><span class="mw-headline">Grands Prix</span></h2></div>
    <div class="mw-heading mw-heading3"><h3 id="Round_results"><span class="mw-headline">Round results</span></h3></div>
    """
    soup = BeautifulSoup(html, "html.parser")

    match = find_section_heading(soup, "Results", domain="seasons")

    assert match is not None
    assert match.strategy in {"exact_id", "exact_text", "fuzzy"}
    assert match.heading.get("id") == "Grands_Prix"
