from scrapers.points.parsers import PointsScoringSystemsHistoryTableParser


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
            "seasons": "1950",
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
            "fastest_lap": "1",
            "towards_wdc": "Yes",
            "towards_wcc": "No",
            "notes": "-",
        },
    ]
