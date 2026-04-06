from scrapers.sponsorship_liveries.parsers.splitters.broader_scope import (
    BroaderScopeSplitter,
)


def test_split_removes_marker_and_splits_overlapping_scope_snapshot() -> None:
    records = [
        {
            "season": [{"year": 2020}, {"year": 2021}],
            "main_colours": ["Black"],
            "_season_scoped_gp": True,
        },
        {
            "season": [{"year": 2021}, {"year": 2022}, {"year": 2023}],
            "main_colours": ["Silver"],
        },
    ]
    season_scoped = [
        {"season": [{"year": 2022}]},
        {"season": [{"year": 2024}]},
    ]

    result = BroaderScopeSplitter(records, season_scoped).split()

    assert result == [
        {
            "season": [{"year": 2020}, {"year": 2021}],
            "main_colours": ["Black"],
        },
        {
            "season": [{"year": 2021}, {"year": 2023}],
            "main_colours": ["Silver"],
        },
        {
            "season": [{"year": 2022}],
            "main_colours": ["Silver"],
            "grand_prix_scope": {"type": "other"},
        },
    ]


def test_split_skips_scope_split_for_driver_records() -> None:
    records = [
        {
            "season": [{"year": 2022}, {"year": 2023}],
            "driver": [{"text": "Driver A"}],
        },
    ]

    result = BroaderScopeSplitter(
        records,
        season_scoped=[{"season": [{"year": 2022}]}],
    ).split()

    assert result == records


def test_split_keeps_record_when_no_season_years_or_overlap() -> None:
    records = [
        {"season": [{"name": "unknown"}], "main_colours": ["Blue"]},
        {"season": [{"year": 1999}], "main_colours": ["Green"]},
    ]

    result = BroaderScopeSplitter(
        records,
        season_scoped=[{"season": [{"year": 2000}]}],
    ).split()

    assert result == records


def test_private_helpers_handle_ambiguous_season_records() -> None:
    record = {
        "season": [{"year": 2025}, {"year": "2026"}, "invalid", {"other": 1}],
    }

    years = BroaderScopeSplitter._years(record)  # noqa: SLF001
    seasons_for_known_year = BroaderScopeSplitter._seasons_for_years(record, {2025})  # noqa: SLF001

    assert years == {2025, "2026"}
    assert seasons_for_known_year == [{"year": 2025}]
