from bs4 import BeautifulSoup

from scrapers.points.parsers import PointsScoringSystemsSectionParser
from scrapers.points.parsers import ShortenedRacesSubSubSectionParser
from scrapers.points.parsers import SpecialCasesSubSectionParser
from scrapers.points.parsers import SprintRacesSubSubSectionParser
from scrapers.points.points_scraper import PointsScraper
from scrapers.wiki.parsers.sections.data_classes import SectionExtractionContext


def test_points_scraper_uses_points_scoring_systems_section_parser() -> None:
    scraper = PointsScraper()
    assert isinstance(scraper.section_parser, PointsScoringSystemsSectionParser)


def test_points_scoring_systems_section_parser_uses_special_cases_subsection_parser(
) -> None:
    parser = PointsScoringSystemsSectionParser()
    assert isinstance(parser.child_parser, SpecialCasesSubSectionParser)


def test_special_cases_subsection_parser_routes_to_required_subsubsection_parsers(
) -> None:
    parser = SpecialCasesSubSectionParser()
    router = parser.child_parser

    assert isinstance(router.sprint_parser, SprintRacesSubSubSectionParser)
    assert isinstance(router.shortened_parser, ShortenedRacesSubSubSectionParser)


def test_shortened_subsubsection_parser_fallback_extracts_table_for_shortened_section(
) -> None:
    html = """
    <div>
      <section>
        <div class="wrapper">
          <table class="wikitable">
            <tr>
              <th>Seasons</th>
              <th>Race length completed</th>
              <th>1st</th>
              <th>2nd</th>
              <th>3rd</th>
              <th>4th</th>
              <th>5th</th>
              <th>6th</th>
              <th>7th</th>
              <th>8th</th>
              <th>9th</th>
              <th>10th</th>
              <th>Fastest lap</th>
              <th>Notes</th>
            </tr>
            <tr>
              <td>2021</td><td>75%</td><td>25</td><td>18</td><td>15</td><td>12</td>
              <td>10</td><td>8</td><td>6</td><td>4</td><td>2</td><td>1</td><td>1</td><td>-</td>
            </tr>
          </table>
        </div>
      </section>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    parser = ShortenedRacesSubSubSectionParser()
    context = SectionExtractionContext(section_id="Shortened_races")

    result = parser.parse_group(list(soup.div.children), context=context)

    def _contains_shortened_table(node: object) -> bool:
        if isinstance(node, dict):
            if node.get("table_type") == "points_shortened_races":
                return True
            return any(_contains_shortened_table(value) for value in node.values())
        if isinstance(node, list):
            return any(_contains_shortened_table(item) for item in node)
        return False

    assert _contains_shortened_table(result)
def test_sprint_parser_parses_table_without_nested_heading() -> None:
    parser = SprintRacesSubSubSectionParser()
    soup = BeautifulSoup(
        """
        <table class="wikitable">
          <tr><th>Season(s)</th><th>1st</th><th>2nd</th><th>3rd</th><th>4th</th><th>5th</th><th>6th</th><th>7th</th><th>8th</th></tr>
          <tr><td>2021–present</td><td>8</td><td>7</td><td>6</td><td>5</td><td>4</td><td>3</td><td>2</td><td>1</td></tr>
        </table>
        """,
        "html.parser",
    )
    parsed = parser.parse_group(soup.find_all("table"))

    top_section = parsed["sub_sub_sub_sections"][0]

    assert top_section["elements"][0]["data"]["table_type"] == "points_sprint_races"
    assert top_section["elements"][0]["data"]["domain_rows"][0]["seasons"] == "2021-present"


def test_special_cases_router_applies_sprint_parser_without_section_hint() -> None:
    parser = SpecialCasesSubSectionParser().child_parser
    soup = BeautifulSoup(
        """
        <table class="wikitable">
          <tr><th>Season(s)</th><th>1st</th><th>2nd</th><th>3rd</th><th>4th</th><th>5th</th><th>6th</th><th>7th</th><th>8th</th></tr>
          <tr><td>2021–present</td><td>8</td><td>7</td><td>6</td><td>5</td><td>4</td><td>3</td><td>2</td><td>1</td></tr>
        </table>
        """,
        "html.parser",
    )
    parsed = parser.parse_group(
        soup.find_all("table"),
        context=SectionExtractionContext(section_id="special_cases"),
    )

    top_section = parsed["sub_sub_sub_sections"][0]
    assert top_section["elements"][0]["data"]["table_type"] == "points_sprint_races"


def test_points_scraper_legacy_sprint_extractor_reads_sprint_races_section() -> None:
    scraper = PointsScraper(export_scope="sprint")
    soup = BeautifulSoup(
        """
        <div id="bodyContent">
          <h3><span id="Sprint_races">Sprint races</span></h3>
          <table class="wikitable">
            <tr>
              <th>Seasons</th><th>1st</th><th>2nd</th><th>3rd</th><th>4th</th><th>5th</th><th>6th</th><th>7th</th><th>8th</th>
            </tr>
            <tr>
              <td>2021–present</td><td>8</td><td>7</td><td>6</td><td>5</td><td>4</td><td>3</td><td>2</td><td>1</td>
            </tr>
          </table>
        </div>
        """,
        "html.parser",
    )

    rows = scraper._extract_sprint_rows_via_legacy_table_scraper(soup)

    assert rows[0]["seasons"][0]["year"] == 2021
    assert rows[0]["1st"] == 8


def test_points_scraper_uses_legacy_fallback_when_nested_parser_has_no_sprint_rows(
    monkeypatch,
) -> None:
    scraper = PointsScraper(export_scope="sprint")
    soup = BeautifulSoup('<div id="bodyContent"></div>', "html.parser")

    monkeypatch.setattr(scraper, "_collect_table_rows", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        scraper,
        "_extract_sprint_rows_via_legacy_table_scraper",
        lambda *_args, **_kwargs: [{"seasons": "2021-present", "1st": "8"}],
    )

    rows = scraper._parse_soup(soup)
    assert rows == [{"seasons": "2021-present", "1st": "8"}]
