from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SectionFixture:
    domain: str
    variant: str
    html: str
    expected_section_id: str
    expected_kind: str


@dataclass(frozen=True)
class SectionContractFixture:
    html: str
    expected_records: list[dict[str, Any]]
    expected_metadata: dict[str, Any]


def _content_text_fixture(
    *,
    h2_id: str,
    h2_text: str,
    h3_id: str,
    h3_text: str,
    body_html: str,
) -> str:
    return f"""
    <div id=\"mw-content-text\" class=\"mw-body-content\">
      <p>Intro</p>
      <div class=\"mw-heading mw-heading2\"><h2 id=\"{h2_id}\">{h2_text}</h2></div>
      <div class=\"mw-heading mw-heading3\"><h3 id=\"{h3_id}\">{h3_text}</h3></div>
      {body_html}
    </div>
    """


def _snapshot_cases_drivers() -> tuple[SectionFixture, SectionFixture]:
    return (
        SectionFixture(
            domain="drivers",
            variant="minimal",
            html=_content_text_fixture(
                h2_id="Career",
                h2_text="Career",
                h3_id="Formula_One",
                h3_text="Formula One",
                body_html="<div><span><p>Debut in 2007.</p></span></div>",
            ),
            expected_section_id="career",
            expected_kind="paragraph",
        ),
        SectionFixture(
            domain="drivers",
            variant="edge",
            html=_content_text_fixture(
                h2_id="Career_results",
                h2_text="Career results",
                h3_id="Racing_record",
                h3_text="Racing record",
                body_html="<span><ul><li><a href='/wiki/2007_Formula_One_World_Championship'>2007</a></li></ul></span>",
            ),
            expected_section_id="career_results",
            expected_kind="list",
        ),
    )


def _snapshot_cases_constructors() -> tuple[SectionFixture, SectionFixture]:
    return (
        SectionFixture(
            domain="constructors",
            variant="minimal",
            html=_content_text_fixture(
                h2_id="Results",
                h2_text="Results",
                h3_id="Championship_results",
                h3_text="Championship results",
                body_html="<div><table class='wikitable'><tr><th>Year</th></tr><tr><td>2024</td></tr></table></div>",
            ),
            expected_section_id="results",
            expected_kind="table",
        ),
        SectionFixture(
            domain="constructors",
            variant="edge",
            html=_content_text_fixture(
                h2_id="Constructors_for_the_current_season",
                h2_text="Constructors for the current season",
                h3_id="Entries",
                h3_text="Entries",
                body_html="<div><figure><img src='constructor.png'/></figure></div>",
            ),
            expected_section_id="constructors_for_the_current_season",
            expected_kind="figure",
        ),
    )


def _snapshot_cases_circuits() -> tuple[SectionFixture, SectionFixture]:
    return (
        SectionFixture(
            domain="circuits",
            variant="minimal",
            html=_content_text_fixture(
                h2_id="Layout",
                h2_text="Layout",
                h3_id="Current",
                h3_text="Current",
                body_html="<figure><img src='x.png'/></figure>",
            ),
            expected_section_id="layout",
            expected_kind="figure",
        ),
        SectionFixture(
            domain="circuits",
            variant="edge",
            html=_content_text_fixture(
                h2_id="Formula_One_circuits",
                h2_text="Formula One circuits",
                h3_id="List",
                h3_text="List",
                body_html="<div><table class='wikitable'><tr><th>Circuit</th></tr><tr><td>Monza</td></tr></table></div>",
            ),
            expected_section_id="formula_one_circuits",
            expected_kind="table",
        ),
    )


def _snapshot_cases_seasons() -> tuple[SectionFixture, SectionFixture]:
    return (
        SectionFixture(
            domain="seasons",
            variant="minimal",
            html=_content_text_fixture(
                h2_id="Grands_Prix",
                h2_text="Grands Prix",
                h3_id="Rounds",
                h3_text="Rounds",
                body_html="<p>24 races.</p>",
            ),
            expected_section_id="grands_prix",
            expected_kind="paragraph",
        ),
        SectionFixture(
            domain="seasons",
            variant="edge",
            html=_content_text_fixture(
                h2_id="Results_and_standings",
                h2_text="Results and standings",
                h3_id="Race_results",
                h3_text="Race results",
                body_html="<span><ul><li>Round 1</li></ul></span>",
            ),
            expected_section_id="results_and_standings",
            expected_kind="list",
        ),
    )


def _snapshot_cases_grands_prix() -> tuple[SectionFixture, SectionFixture]:
    return (
        SectionFixture(
            domain="grands_prix",
            variant="minimal",
            html=_content_text_fixture(
                h2_id="Race",
                h2_text="Race",
                h3_id="Classification",
                h3_text="Classification",
                body_html="<span><ul><li>P1</li></ul></span>",
            ),
            expected_section_id="race",
            expected_kind="list",
        ),
        SectionFixture(
            domain="grands_prix",
            variant="edge",
            html=_content_text_fixture(
                h2_id="Race",
                h2_text="Race",
                h3_id="Fastest_lap",
                h3_text="Fastest lap",
                body_html="<div><table class='wikitable'><tr><th>Driver</th></tr><tr><td>Max Verstappen</td></tr></table></div>",
            ),
            expected_section_id="race",
            expected_kind="table",
        ),
    )


SNAPSHOT_CASES_BY_DOMAIN: dict[str, tuple[SectionFixture, SectionFixture]] = {
    "drivers": _snapshot_cases_drivers(),
    "constructors": _snapshot_cases_constructors(),
    "circuits": _snapshot_cases_circuits(),
    "seasons": _snapshot_cases_seasons(),
    "grands_prix": _snapshot_cases_grands_prix(),
}


def iter_snapshot_cases() -> list[SectionFixture]:
    return [
        fixture
        for fixtures in SNAPSHOT_CASES_BY_DOMAIN.values()
        for fixture in fixtures
    ]


def assert_section_contract_template(
    result: Any,
    fixture: SectionContractFixture,
) -> None:
    assert result.records == fixture.expected_records
    for key, expected_value in fixture.expected_metadata.items():
        assert result.metadata[key] == expected_value


SECTION_MODULES_REQUIRING_DOD: tuple[str, ...] = tuple(
    sorted(
        str(path).replace("\\", "/")
        for path in Path("scrapers").glob("*/sections/*.py")
        if path.name != "__init__.py"
        and path.parts[1]
        in {"drivers", "constructors", "circuits", "seasons", "grands_prix"}
    ),
)

SNAPSHOT_COVERED_SECTION_MODULES: tuple[str, ...] = (
    "scrapers/circuits/sections/events.py",
    "scrapers/circuits/sections/lap_records.py",
    "scrapers/circuits/sections/layout_history.py",
    "scrapers/circuits/sections/list_section.py",
    "scrapers/constructors/sections/championship_results.py",
    "scrapers/constructors/sections/common.py",
    "scrapers/constructors/sections/complete_f1_results.py",
    "scrapers/constructors/sections/history.py",
    "scrapers/constructors/sections/list_section.py",
    "scrapers/drivers/sections/career.py",
    "scrapers/drivers/sections/non_championship.py",
    "scrapers/drivers/sections/racing_record.py",
    "scrapers/drivers/sections/results.py",
    "scrapers/grands_prix/sections/by_year.py",
    "scrapers/seasons/sections/calendar.py",
    "scrapers/seasons/sections/contracts.py",
    "scrapers/seasons/sections/mid_season_changes.py",
    "scrapers/seasons/sections/regulation_changes.py",
    "scrapers/seasons/sections/results.py",
    "scrapers/seasons/sections/standings.py",
)

CONTRACT_COVERED_SECTION_MODULES: tuple[str, ...] = SNAPSHOT_COVERED_SECTION_MODULES

ALIAS_FIXTURES: dict[str, str] = {
    "constructors": """
    <html><body>
    <h2><span id=\"Constructors_for_the_current_season\">Constructors for the current season</span></h2>
    <table class=\"wikitable\">
    <tr><th>Constructor</th><th>Engine</th><th>Licensed in</th><th>Based in</th></tr>
    <tr>
    <td><a href=\"/wiki/Ferrari\">Ferrari</a></td>
    <td><a href=\"/wiki/Ferrari_059/6\">Ferrari</a></td>
    <td>Italy</td>
    <td><a href=\"/wiki/Maranello\">Maranello</a></td>
    </tr>
    </table>
    </body></html>
    """,
    "circuits": """
    <html><body>
    <h2><span id=\"Formula_One_circuits\">Formula One circuits</span></h2>
    <table class=\"wikitable\">
    <tr><th>Circuit</th><th>Type</th><th>Location</th><th>Country</th></tr>
    <tr>
    <td><a href=\"/wiki/Monza_Circuit\">Monza</a></td>
    <td>Permanent</td>
    <td>Monza</td>
    <td><a href=\"/wiki/Italy\">Italy</a></td>
    </tr>
    </table>
    </body></html>
    """,
    "seasons": """
    <div id=\"bodyContent\">
      <div id=\"mw-content-text\" class=\"mw-body-content\">
        <div class=\"mw-heading mw-heading2\"><h2 id=\"Results_and_standings\">Results and standings</h2></div>
        <div class=\"mw-heading mw-heading3\"><h3 id=\"Rounds\">Rounds</h3></div>
        <table class=\"wikitable\">
          <tr><th>Round</th><th>Grand Prix</th><th>Fastest lap</th><th>Winning driver</th><th>Report</th></tr>
          <tr>
            <td>1</td>
            <td><a href=\"/wiki/Bahrain_Grand_Prix\">Bahrain Grand Prix</a></td>
            <td>Max Verstappen</td>
            <td>Max Verstappen</td>
            <td><a href=\"/wiki/2024_Bahrain_Grand_Prix\">Report</a></td>
          </tr>
        </table>
      </div>
    </div>
    """,
}
