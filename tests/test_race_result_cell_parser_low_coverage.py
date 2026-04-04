from bs4 import BeautifulSoup
import pytest

from scrapers.base.table.columns.context import ColumnContext
from scrapers.seasons.columns.helpers.constants import SPRINT_POINTS_START_YEAR
from scrapers.seasons.columns.helpers.race_result.cell_parser import RaceResultCellParser


@pytest.mark.parametrize(
    ("raw_text", "expected"),
    [
        ("1/2", [{"position": 1}, {"position": 2}]),
        ("RET† ; --", [{"position": "RET ; --", "marks": ["†"]}]),
        ("(3*)", [{"position": 3, "marks": ["*"], "points_counted": False}]),
        ("", []),
    ],
)
def test_parse_results_covers_happy_path_and_weird_separators(raw_text: str, expected: list[dict]) -> None:
    parser = RaceResultCellParser()

    assert parser.parse_results(raw_text) == expected


def test_extract_result_text_falls_back_to_clean_text_when_cell_missing() -> None:
    parser = RaceResultCellParser()
    ctx = ColumnContext(
        header="Race",
        key="result",
        raw_text=None,
        clean_text="  DNS  ",
        links=[],
        cell=None,
        base_url="https://example.test",
    )

    assert parser.extract_result_text(ctx) == "DNS"


@pytest.mark.parametrize(
    ("season_year", "expected_sprint", "expected_footnotes"),
    [
        (SPRINT_POINTS_START_YEAR, 2, ["1"]),
        (SPRINT_POINTS_START_YEAR - 1, None, ["1", "2"]),
        (None, None, ["1", "2"]),
    ],
)
def test_parse_superscripts_handles_rule_conflicts_and_year_priority(
    season_year: int | None,
    expected_sprint: int | None,
    expected_footnotes: list[str],
) -> None:
    parser = RaceResultCellParser()
    soup = BeautifulSoup(
        '<td><b>1</b><i>fast</i><sup>1PF</sup><sup>2</sup></td>',
        'html.parser',
    )
    ctx = ColumnContext(
        header="Race",
        key="result",
        raw_text="1",
        clean_text="1",
        links=[],
        cell=soup.td,
        base_url="https://example.test",
    )

    result = parser.parse_superscripts(ctx, season_year=season_year)

    # Asercje na strukturę pośrednią (SuperscriptParseResult)
    assert result.sprint_position == expected_sprint
    assert result.pole_position is True
    assert result.fastest_lap is True
    assert result.footnotes == expected_footnotes


def test_prepare_cell_fragment_strips_absolute_spans_and_superscripts() -> None:
    parser = RaceResultCellParser()
    soup = BeautifulSoup(
        '<td><span style="position: absolute; left:-9999px">ghost</span> 4<sup>7</sup></td>',
        'html.parser',
    )

    fragment = parser._prepare_cell_fragment(soup.td)

    assert "ghost" not in fragment.get_text(" ", strip=True)
    assert "7" not in fragment.get_text(" ", strip=True)
