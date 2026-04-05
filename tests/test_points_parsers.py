from scrapers.points.parsers import PointsScoringSystemsHistoryTableParser
from scrapers.points.parsers import ShortenedRacesPointsTableParser


def test_points_history_parser_accepts_championship_alias_headers() -> None:
    parser = PointsScoringSystemsHistoryTableParser()
    table_data = {
        "headers": [
            "Seasons",
            "1st",
            "2nd",
            "3rd",
            "4th",
            "5th",
            "6th",
            "7th",
            "8th",
            "9th",
            "10th",
            "Fastest lap",
            "Drivers' Championship",
            "Constructors' Championship",
            "Notes",
        ],
        "rows": [
            {
                "Seasons": "1950",
                "1st": "8",
                "2nd": "6",
                "3rd": "4",
                "4th": "3",
                "5th": "2",
                "6th": "0",
                "7th": "0",
                "8th": "0",
                "9th": "0",
                "10th": "0",
                "Fastest lap": "1",
                "Drivers' Championship": "Yes",
                "Constructors' Championship": "No",
                "Notes": "-",
            },
        ],
    }

    parsed = parser.parse(table_data)

    assert parsed is not None
    assert parsed["table_type"] == "points_scoring_systems_history"
    assert parsed["domain_rows"] == [
        {
            "seasons": [
                {
                    "year": 1950,
                    "url": "https://en.wikipedia.org/wiki/1950_Formula_One_World_Championship",
                },
            ],
            "1st": 8,
            "2nd": 6,
            "3rd": 4,
            "4th": 3,
            "5th": 2,
            "6th": 0,
            "7th": 0,
            "8th": 0,
            "9th": 0,
            "10th": 0,
            "fastest_lap": 1,
            "drivers_championship": "Yes",
            "constructors_championship": "No",
        },
    ]


_SHORTENED_HEADERS = [
    "Seasons",
    "Race length completed",
    "1st",
    "2nd",
    "3rd",
    "4th",
    "5th",
    "6th",
    "7th",
    "8th",
    "9th",
    "10th",
    "Fastest lap",
    "Notes",
]

_EXPECTED_TWO_ROWS = 2
_YEAR_1975 = 1975
_YEAR_1976 = 1976
_YEAR_2022 = 2022


def test_shortened_races_parser_groups_rows_by_seasons() -> None:
    parser = ShortenedRacesPointsTableParser()
    table_data = {
        "headers": _SHORTENED_HEADERS,
        "rows": [
            {
                "Seasons": "1975-1976",
                "Race length completed": "Less than 30%",
                "1st": "-",
                "2nd": "-",
                "3rd": "-",
                "4th": "-",
                "5th": "-",
                "6th": "-",
                "7th": "-",
                "8th": "-",
                "9th": "-",
                "10th": "-",
                "Fastest lap": "-",
                "Notes": None,
            },
            {
                "Seasons": "1975-1976",
                "Race length completed": "Between 30% and 60%",
                "1st": "Half",
                "2nd": "Half",
                "3rd": "Half",
                "4th": "Half",
                "5th": "Half",
                "6th": "Half",
                "7th": "Half",
                "8th": "Half",
                "9th": "Half",
                "10th": "Half",
                "Fastest lap": "-",
                "Notes": None,
            },
        ],
    }

    parsed = parser.parse(table_data)

    assert parsed is not None
    assert parsed["table_type"] == "points_shortened_races"
    assert len(parsed["domain_rows"]) == 1
    group = parsed["domain_rows"][0]
    assert group["seasons"] == [
        {
            "year": 1975,
            "url": "https://en.wikipedia.org/wiki/1975_Formula_One_World_Championship",
        },
        {
            "year": 1976,
            "url": "https://en.wikipedia.org/wiki/1976_Formula_One_World_Championship",
        },
    ]
    assert len(group["race_length_points"]) == _EXPECTED_TWO_ROWS
    assert group["race_length_points"][0] == {
        "race_length_completed": "Less than 30%",
        "1st": "-",
        "2nd": "-",
        "3rd": "-",
        "4th": "-",
        "5th": "-",
        "6th": "-",
        "7th": "-",
        "8th": "-",
        "9th": "-",
        "10th": "-",
        "fastest_lap": "-",
    }
    assert "seasons" not in group["race_length_points"][0]
    assert "notes" not in group["race_length_points"][0]


def test_shortened_races_parser_produces_multiple_season_groups() -> None:
    parser = ShortenedRacesPointsTableParser()
    table_data = {
        "headers": _SHORTENED_HEADERS,
        "rows": [
            {
                "Seasons": "1975-1976",
                "Race length completed": "Less than 30%",
                "1st": "-",
                "2nd": "-",
                "3rd": "-",
                "4th": "-",
                "5th": "-",
                "6th": "-",
                "7th": "-",
                "8th": "-",
                "9th": "-",
                "10th": "-",
                "Fastest lap": "-",
                "Notes": None,
            },
            {
                "Seasons": "2022 onwards",
                "Race length completed": "Less than two full racing laps",
                "1st": "-",
                "2nd": "-",
                "3rd": "-",
                "4th": "-",
                "5th": "-",
                "6th": "-",
                "7th": "-",
                "8th": "-",
                "9th": "-",
                "10th": "-",
                "Fastest lap": "-",
                "Notes": None,
            },
            {
                "Seasons": "2022 onwards",
                "Race length completed": "Between two full racing laps and 25%",
                "1st": "6",
                "2nd": "4",
                "3rd": "3",
                "4th": "2",
                "5th": "1",
                "6th": "-",
                "7th": "-",
                "8th": "-",
                "9th": "-",
                "10th": "-",
                "Fastest lap": "-",
                "Notes": None,
            },
        ],
    }

    parsed = parser.parse(table_data)

    assert parsed is not None
    assert len(parsed["domain_rows"]) == _EXPECTED_TWO_ROWS
    assert parsed["domain_rows"][0]["seasons"][0]["year"] == _YEAR_1975
    assert parsed["domain_rows"][0]["seasons"][1]["year"] == _YEAR_1976
    assert len(parsed["domain_rows"][0]["race_length_points"]) == 1
    assert len(parsed["domain_rows"][1]["race_length_points"]) == _EXPECTED_TWO_ROWS
    assert parsed["domain_rows"][1]["seasons"][0]["year"] == _YEAR_2022
