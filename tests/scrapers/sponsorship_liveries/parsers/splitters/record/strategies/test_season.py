# ruff: noqa: SLF001
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries import PipelineRecord
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries import (
    SeasonSplitStrategy,
)


def test_apply_returns_original_for_single_season_record() -> None:
    record = PipelineRecord.from_input(
        {
            "season": [{"year": 2025}],
            "main_colours": ["Papaya"],
            "main_sponsors": [{"text": "ACME"}],
        },
    )

    result = SeasonSplitStrategy().apply(record)

    assert result == [record]


def test_apply_splits_year_range_sponsors_and_colours_snapshot() -> None:
    record = PipelineRecord.from_input(
        {
            "season": [{"year": 2024}, {"year": 2025}, {"year": 2026}],
            "main_colours": ["Orange", "Special Blue (2024-2025)", "Pink (2026)"],
            "main_sponsors": [
                {"text": "Base"},
                {"text": "Partner A", "params": ["2024-2025"]},
                {"text": "Partner B", "params": ["2026"]},
            ],
        },
    )

    result = SeasonSplitStrategy().apply(record)

    assert [r.payload for r in result] == [
        {
            "season": [{"year": 2024}],
            "main_colours": ["Orange", "Special Blue"],
            "main_sponsors": [{"text": "Base"}, {"text": "Partner A"}],
        },
        {
            "season": [{"year": 2025}],
            "main_colours": ["Orange", "Special Blue"],
            "main_sponsors": [{"text": "Base"}, {"text": "Partner A"}],
        },
        {
            "season": [{"year": 2026}],
            "main_colours": ["Orange", "Pink"],
            "main_sponsors": [{"text": "Base"}, {"text": "Partner B"}],
        },
    ]


def test_apply_splits_mixed_text_parentheses_and_separators_by_colour_scope() -> None:
    record = PipelineRecord.from_input(
        {
            "season": [{"year": 2020}, {"year": 2021}, {"year": 2022}],
            "main_colours": [
                "Silver and Black",
                "Neon (2020)",
                "White/Red (2021)",
            ],
            "main_sponsors": [{"text": "No year params"}],
        },
    )

    result = SeasonSplitStrategy().apply(record)

    assert [r.payload for r in result] == [
        {
            "season": [{"year": 2022}],
            "main_colours": ["Silver and Black"],
            "main_sponsors": [{"text": "No year params"}],
        },
        {
            "season": [{"year": 2020}],
            "main_colours": ["Silver and Black", "Neon"],
            "main_sponsors": [{"text": "No year params"}],
        },
        {
            "season": [{"year": 2021}],
            "main_colours": ["Silver and Black", "White/Red"],
            "main_sponsors": [{"text": "No year params"}],
        },
    ]


def test_colour_scope_helpers_cover_ambiguous_and_duplicate_sets() -> None:
    season_entries = [{"year": 2020}, {"year": 2021}]
    record = PipelineRecord.from_input(
        {
            "season": season_entries,
            "main_colours": [
                "Blue (2020)",
                "Green (2020)",
                "Unused (2028)",
                7,
            ],
        },
    )

    ambiguous = PipelineRecord.from_input(
        {"season": season_entries, "main_colours": ["Plain", 1]},
    )

    assert SeasonSplitStrategy._season_entries("2020") == []
    assert SeasonSplitStrategy._extract_colour_year_sets(ambiguous) == []
    assert SeasonSplitStrategy._split_record_by_colour_scopes(
        ambiguous,
        season_entries,
    ) == [ambiguous]

    year_sets = SeasonSplitStrategy._extract_colour_year_sets(record)
    unique_year_sets = SeasonSplitStrategy._unique_year_sets(year_sets)
    assert unique_year_sets == [{2020}, {2028}]

    base_split = SeasonSplitStrategy._build_base_colour_scoped_records(
        record,
        season_entries,
        year_sets,
    )
    assert [r.payload for r in base_split] == [
        {
            "season": [{"year": 2021}],
            "main_colours": [7],
        },
    ]

    scoped_split = SeasonSplitStrategy._build_year_scoped_colour_records(
        record,
        season_entries,
        year_sets,
    )
    assert [r.payload for r in scoped_split] == [
        {
            "season": [{"year": 2020}],
            "main_colours": ["Blue", "Green", 7],
        },
    ]

    assert (
        SeasonSplitStrategy._build_base_colour_scoped_records(
            record,
            season_entries=[{"year": 2020}],
            colour_year_sets=[{2020}],
        )
        == []
    )

    assert (
        SeasonSplitStrategy._build_year_scoped_colour_records(
            record,
            season_entries=[{"year": 2020}],
            colour_year_sets=[{2030}],
        )
        == []
    )
