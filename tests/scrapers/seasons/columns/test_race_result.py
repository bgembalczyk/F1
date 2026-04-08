from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.seasons.columns.race_result import RaceResultColumn


def ctx(
    cell_html: str,
    *,
    header: str = "R1",
    header_link: dict | None = None,
) -> ColumnContext:
    cell = BeautifulSoup(cell_html, "html.parser").find("td")
    return ColumnContext(
        header=header,
        key="race_result",
        raw_text=cell.get_text(" ", strip=True) if cell else "",
        clean_text=cell.get_text(" ", strip=True) if cell else "",
        links=[],
        cell=cell,
        base_url="https://en.wikipedia.org",
        header_link=header_link,
    )


# ---------------------------------------------------------------------------
# parsowanie podstawowe
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("cell_html", "expected_positions"),
    [
        ("<td>1</td>", [1]),
        ("<td>1 / 2</td>", [1, 2]),
        ("<td>(3)</td>", [3]),
        ("<td>4† / 5*</td>", [4, 5]),
    ],
)
def test_parse_supports_multiple_result_table_formats(
    cell_html: str,
    expected_positions: list[int],
) -> None:
    parsed = RaceResultColumn(season_year=1960).parse(ctx(cell_html))

    assert parsed is not None
    assert [item["position"] for item in parsed["results"]] == expected_positions


def test_parse_attaches_round_link_and_marks_pole_and_fastest_lap() -> None:
    parsed = RaceResultColumn(season_year=2023).parse(
        ctx(
            '<td style="background:#ffffbf"><b><i>1</i></b></td>',
            header_link={
                "text": "Bahrain Grand Prix",
                "url": "https://en.wikipedia.org/wiki/2023_Bahrain_Grand_Prix",
            },
        ),
    )

    assert parsed is not None
    assert parsed["round"]["text"] == "Bahrain Grand Prix"
    assert parsed["results"][0]["background"] == "Winner"
    assert parsed["results"][0]["pole_position"] is True
    assert parsed["results"][0]["fastest_lap"] is True


def test_parse_promotes_single_result_with_sprint_position_to_scalar_payload() -> None:
    parsed = RaceResultColumn(season_year=2023).parse(ctx("<td>5<sup>2</sup></td>"))

    assert parsed is not None
    assert isinstance(parsed["results"], dict)
    assert parsed["results"]["position"] == 5  # noqa: PLR2004
    assert parsed["results"]["sprint_position"] == 2  # noqa: PLR2004


# ---------------------------------------------------------------------------
# reguły specjalne
# ---------------------------------------------------------------------------


def test_parse_adds_half_points_round_note_for_marked_header() -> None:
    parsed = RaceResultColumn(season_year=1975).parse(
        ctx(
            "<td>2</td>",
            header="Spanish Grand Prix*",
            header_link={
                "url": "https://en.wikipedia.org/wiki/1975_Spanish_Grand_Prix",
            },
        ),
    )

    assert parsed is not None
    assert parsed["round"]["note"] == "half_points"
    assert parsed["round"]["points_multiplier"] == 0.5  # noqa: PLR2004


def test_parse_adds_double_points_round_note_for_2014_abu_dhabi() -> None:
    parsed = RaceResultColumn(season_year=2014).parse(
        ctx(
            "<td>1</td>",
            header="Abu Dhabi‡",
            header_link={
                "url": "https://en.wikipedia.org/wiki/2014_Abu_Dhabi_Grand_Prix",
            },
        ),
    )

    assert parsed is not None
    assert parsed["round"]["note"] == "double_points"
    assert parsed["round"]["points_multiplier"] == 2.0  # noqa: PLR2004


def test_parse_marks_shared_drive_and_share_count_when_two_results_present() -> None:
    parsed = RaceResultColumn(season_year=1957).parse(ctx("<td>1† / 2†</td>"))

    assert parsed is not None
    assert parsed["results"][0]["shared_drive"] is True
    assert parsed["results"][0]["points_shared"] is True
    assert parsed["results"][0]["points_share_count"] == 2  # noqa: PLR2004


# ---------------------------------------------------------------------------
# edge cases (DNS/DNF/DSQ, brak pola, tie)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", ["DNS", "DNF", "DSQ"])
def test_parse_preserves_status_codes(status: str) -> None:
    parsed = RaceResultColumn(season_year=1970).parse(ctx(f"<td>{status}</td>"))

    assert parsed is not None
    assert parsed["results"][0]["position"] == status


def test_parse_returns_none_for_empty_result_cell() -> None:
    assert RaceResultColumn(season_year=1970).parse(ctx("<td> </td>")) is None


def test_parse_returns_none_for_only_missing_markers_without_background() -> None:
    assert RaceResultColumn(season_year=1970).parse(ctx("<td>- / --</td>")) is None


def test_parse_keeps_tie_like_text_position() -> None:
    parsed = RaceResultColumn(season_year=1970).parse(ctx("<td>T1</td>"))

    assert parsed is not None
    assert parsed["results"][0]["position"] == "T1"


def test_parse_translates_nc_with_other_classified_background() -> None:
    parsed = RaceResultColumn(season_year=1970).parse(
        ctx('<td style="background:#cfcfff">NC</td>'),
    )

    assert parsed is not None
    assert parsed["results"][0]["background"] == "Not classified, finished"
