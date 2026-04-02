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
