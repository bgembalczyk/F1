from scrapers.points.parsers import PointsScoringSystemsSectionParser
from scrapers.points.parsers import ShortenedRacesSubSubSectionParser
from scrapers.points.parsers import SpecialCasesSubSectionParser
from scrapers.points.parsers import SprintRacesSubSubSectionParser
from scrapers.points.points_scraper import PointsScraper


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
