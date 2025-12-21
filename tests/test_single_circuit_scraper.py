from bs4 import BeautifulSoup

from scrapers.circuits.single_scraper import F1SingleCircuitScraper


def test_is_circuit_like_article_true_when_category_matches() -> None:
    scraper = F1SingleCircuitScraper()
    soup = BeautifulSoup(
        """
        <div id="mw-normal-catlinks">
            <a href="/wiki/Category:Formula_One_circuits">Formula One circuits</a>
        </div>
        """,
        "html.parser",
    )

    assert scraper._is_circuit_like_article(soup) is True


def test_is_circuit_like_article_false_without_categories() -> None:
    scraper = F1SingleCircuitScraper()
    soup = BeautifulSoup("<div>No categories here</div>", "html.parser")

    assert scraper._is_circuit_like_article(soup) is False


def test_select_section_returns_fragment_section_only() -> None:
    scraper = F1SingleCircuitScraper()
    soup = BeautifulSoup(
        """
        <h2 id="History">History</h2>
        <p>Some history text.</p>
        <h2 id="Legacy">Legacy</h2>
        <p>Legacy text.</p>
        """,
        "html.parser",
    )

    section = scraper._select_section(soup, "History")

    assert "Some history text." in section.get_text(" ")
    assert "Legacy text." not in section.get_text(" ")


def test_select_section_returns_full_soup_when_missing_fragment() -> None:
    scraper = F1SingleCircuitScraper()
    soup = BeautifulSoup(
        """
        <h2 id="History">History</h2>
        <p>Some history text.</p>
        <h2 id="Legacy">Legacy</h2>
        <p>Legacy text.</p>
        """,
        "html.parser",
    )

    section = scraper._select_section(soup, "Unknown")

    assert "Some history text." in section.get_text(" ")
    assert "Legacy text." in section.get_text(" ")
