from pathlib import Path

from bs4 import BeautifulSoup

from scrapers.base.helpers.html_utils import find_heading
from scrapers.wiki.parsers.section_alias_registry import get_alias_telemetry
from scrapers.wiki.parsers.section_alias_registry import reset_alias_telemetry


def _load_fixture(name: str) -> BeautifulSoup:
    fixture = Path("tests/fixtures/section_aliases") / name
    return BeautifulSoup(fixture.read_text(encoding="utf-8"), "html.parser")


def test_drivers_alias_regression_fixture() -> None:
    reset_alias_telemetry()
    soup = _load_fixture("drivers.html")

    heading = find_heading(soup, "Career_results", domain="drivers")

    assert heading is not None
    assert heading.get_text(" ", strip=True) == "Racing record"
    telemetry = get_alias_telemetry()
    assert telemetry[("drivers", "career results", "racing record", "exact_id")] == 1


def test_seasons_alias_regression_fixture() -> None:
    reset_alias_telemetry()
    soup = _load_fixture("seasons.html")

    heading = find_heading(soup, "Results", domain="seasons")

    assert heading is not None
    assert heading.get_text(" ", strip=True) == "Grands Prix"
    telemetry = get_alias_telemetry()
    assert telemetry[("seasons", "results", "grands prix", "exact_id")] == 1


def test_grands_prix_alias_regression_fixture() -> None:
    reset_alias_telemetry()
    soup = _load_fixture("grands_prix.html")

    heading = find_heading(soup, "By_year", domain="grands_prix")

    assert heading is not None
    assert heading.get_text(" ", strip=True) == "Winners"
    telemetry = get_alias_telemetry()
    assert telemetry[("grands_prix", "by year", "winners", "exact_id")] == 1
