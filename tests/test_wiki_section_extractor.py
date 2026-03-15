from bs4 import BeautifulSoup

from scrapers.wiki.parsers.sections.extractor import WikiSectionExtractor
from scrapers.wiki.scraper import WikiScraper


def test_extractor_supports_mw_heading_layout() -> None:
    soup = BeautifulSoup(
        """
        <div>
          <div class="mw-heading mw-heading2"><h2 id="History">History</h2></div>
          <p>Some history text.</p>
          <div class="mw-heading mw-heading3"><h3 id="Legacy">Legacy</h3></div>
          <p>Legacy text.</p>
          <div class="mw-heading mw-heading2"><h2 id="Layouts">Layouts</h2></div>
          <p>Layouts text.</p>
        </div>
        """,
        "html.parser",
    )

    section = WikiSectionExtractor().find_by_fragment(soup, "History")

    assert section is not None
    assert section.heading_id == "History"
    assert section.heading_level == 2
    assert "Some history text." in section.soup.get_text(" ")
    assert "Legacy text." in section.soup.get_text(" ")
    assert "Layouts text." not in section.soup.get_text(" ")


def test_extractor_supports_classic_heading_layout() -> None:
    soup = BeautifulSoup(
        """
        <div>
          <h2 id="History">History</h2>
          <p>Some history text.</p>
          <h3 id="Legacy">Legacy</h3>
          <p>Legacy text.</p>
          <h2 id="Layouts">Layouts</h2>
          <p>Layouts text.</p>
        </div>
        """,
        "html.parser",
    )

    section = WikiSectionExtractor().find_by_fragment(soup, "History")

    assert section is not None
    assert section.heading_id == "History"
    assert section.heading_level == 2
    assert "Some history text." in section.soup.get_text(" ")
    assert "Legacy text." in section.soup.get_text(" ")
    assert "Layouts text." not in section.soup.get_text(" ")


def test_wiki_scraper_find_section_is_single_entry_point() -> None:
    scraper = WikiScraper()
    soup = BeautifulSoup(
        """
        <div>
          <h2 id="Career_results">Career results</h2>
          <p>Career section</p>
          <h2 id="Legacy">Legacy</h2>
          <p>Legacy section</p>
        </div>
        """,
        "html.parser",
    )

    section = scraper.find_section(soup, "Career_results")

    assert section is not None
    assert section.heading_id == "Career_results"
    assert "Career section" in section.soup.get_text(" ")
    assert "Legacy section" not in section.soup.get_text(" ")
