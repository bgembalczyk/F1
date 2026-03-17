import json
from pathlib import Path

from scrapers.wiki.layer_zero_merge import merge_layer_zero_raw_outputs


def _team_text(record: dict[str, object]) -> str:
    team = record.get("team")
    if isinstance(team, dict):
        value = team.get("text")
        return value if isinstance(value, str) else ""
    return team if isinstance(team, str) else ""


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_merge_layer_zero_raw_outputs_merges_and_transforms_domain_json_files(
    tmp_path: Path,
) -> None:
    base_wiki_dir = tmp_path / "data" / "wiki"

    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "circuits" / "raw" / "a.json",
        [
            {
                "circuit": "Monza",
                "turns": 11,
                "circuit_status": "active",
                "grands_prix": ["Italian Grand Prix"],
            },
        ],
    )
    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "constructors" / "raw" / "a.json",
        [
            {
                "constructor": "Ferrari",
                "licensed_in": "Italy",
                "engine": "Ferrari",
                "wins": 248,
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "constructors"
        / "raw"
        / "f1_constructor_standings.json",
        [
            {
                "constructor": "McLaren",
                "wins": 2,
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "constructors"
        / "raw"
        / "f1_former_constructors.json",
        [
            {
                "constructor": {"text": "Team Old", "url": "https://example.com/old"},
                "wins": 0,
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "constructors"
        / "raw"
        / "f1_indianapolis_only_constructors.json",
        [
            {
                "constructor": "Indy Team",
                "constructor_url": "https://example.com/indy",
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "drivers"
        / "raw"
        / "female_drivers.json",
        [{"driver": {"text": "Maria", "url": "https://example.com/maria"}}],
    )
    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "drivers" / "raw" / "drivers.json",
        [
            {"driver": {"text": "Max Verstappen", "url": "https://example.com/max"}},
            {"driver": {"text": "Lewis Hamilton", "url": "https://example.com/lewis"}},
            {
                "driver": {
                    "text": "Giovanna Amati",
                    "url": "https://en.wikipedia.org/wiki/Giovanna_Amati",
                },
                "race_entries": 3,
                "nationality": "Italy",
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "drivers"
        / "raw"
        / "f1_women_drivers_who_entered_a_formula_one_race.json",
        [
            {
                "driver": {
                    "text": "Giovanna Amati",
                    "url": "https://en.wikipedia.org/wiki/Giovanna_Amati",
                },
                "entries": 3,
                "teams": [
                    {"text": "Brabham", "url": "https://en.wikipedia.org/wiki/Brabham"},
                ],
            },
            {
                "driver": {
                    "text": "Bob Anderson",
                    "url": "https://en.wikipedia.org/wiki/Bob_Anderson_(racing_driver)",
                },
                "is_active": False,
                "race_entries": 29,
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "drivers"
        / "raw"
        / "f1_driver_fatalities.json",
        [
            {
                "driver": {"text": "X", "url": "https://example.com/x"},
                "date": "2000-01-01",
                "age": 28,
                "event": "test",
                "circuit": "Monza",
                "car": "Car",
                "session": "Practice",
            },
            {
                "driver": {
                    "text": "Bob Anderson",
                    "url": "https://en.wikipedia.org/wiki/Bob_Anderson_(racing_driver)",
                },
                "date": "1967-08-14",
                "age": 36,
                "event": "Test",
                "circuit": "Silverstone",
                "car": "Brabham BT11",
                "session": "Test",
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "races"
        / "raw"
        / "f1_red_flagged_world_championship_races.json",
        [
            {
                "season": 1971,
                "grand_prix": "Canadian",
                "lap": 64,
                "winner": "Stewart",
                "failed_to_make_restart": {"drivers": ["A"], "reason": "Crash"},
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "races"
        / "raw"
        / "f1_red_flagged_non_championship_races.json",
        [
            {
                "season": 1971,
                "event": "Victory Race",
                "lap": 15,
                "incident": "Crash",
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "engines"
        / "raw"
        / "f1_engine_manufacturers.json",
        [
            {
                "manufacturer": "Ferrari",
                "manufacturer_status": "active",
                "wins": 200,
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "engines"
        / "raw"
        / "f1_indianapolis_only_engine_manufacturers.json",
        [{"manufacturer": "Offy"}],
    )
    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "grands_prix" / "raw" / "a.json",
        [{"grand_prix": "Italian", "race_status": "active", "total": 74}],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "teams"
        / "raw"
        / "f1_sponsorship_liveries.json",
        [{"team": "Ferrari", "liveries": ["Marlboro"]}],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "teams"
        / "raw"
        / "f1_privateer_teams.json",
        [{"team": "Rob Walker", "seasons": ["1950"]}],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "teams"
        / "raw"
        / "f1_constructors_2026.json",
        [
            {
                "constructor": {"text": "Team X", "url": "https://example.com/team-x"},
                "engine": {"text": "Engine X", "url": "https://example.com/engine-x"},
                "wins": 1,
            },
            {
                "constructor": {
                    "text": "Cadillac",
                    "url": "https://en.wikipedia.org/wiki/Cadillac_in_Formula_One",
                },
                "engine": [
                    {
                        "text": "Ferrari",
                        "url": "https://en.wikipedia.org/wiki/Scuderia_Ferrari",
                    },
                ],
                "wins": 0,
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "teams"
        / "raw"
        / "cadillac_livery.json",
        [
            {
                "team": {
                    "text": "Cadillac",
                    "url": "https://en.wikipedia.org/wiki/Cadillac_in_Formula_One",
                },
                "racing_series": {
                    "formula_one": {
                        "liveries": [
                            {
                                "main_colours": ["White", "Black"],
                            },
                        ],
                    },
                },
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "teams"
        / "raw"
        / "audi_constructor.json",
        [
            {
                "team": {
                    "text": "Audi",
                    "url": "https://en.wikipedia.org/wiki/Audi_in_Formula_One",
                },
                "racing_series": {
                    "formula_one": {
                        "wins": 0,
                    },
                },
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "teams"
        / "raw"
        / "audi_livery.json",
        [
            {
                "team": "Audi",
                "racing_series": {
                    "formula_one": {
                        "liveries": [
                            {
                                "main_colours": ["Silver", "Red", "Black"],
                            },
                        ],
                    },
                },
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "teams"
        / "raw"
        / "racing_bulls_constructor.json",
        [
            {
                "team": {
                    "text": "Racing Bulls",
                    "url": "https://en.wikipedia.org/wiki/Racing_Bulls",
                },
                "racing_series": {
                    "formula_one": {
                        "seasons": [
                            {
                                "year": 2024,
                                "url": "https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship",
                            },
                            {
                                "year": 2025,
                                "url": "https://en.wikipedia.org/wiki/2025_Formula_One_World_Championship",
                            },
                        ],
                        "wins": 0,
                    },
                },
            },
        ],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "teams"
        / "raw"
        / "racing_bulls_livery.json",
        [
            {
                "team": {
                    "text": "Racing Bulls",
                    "url": "https://en.wikipedia.org/wiki/Racing_Bulls",
                },
                "racing_series": {
                    "formula_one": {
                        "liveries": [
                            {
                                "season": [
                                    {
                                        "year": 2024,
                                        "url": "https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship",
                                    },
                                ],
                                "main_colours": ["Blue", "White"],
                                "special_liveries": "Miami",
                            },
                            {
                                "season": [
                                    {
                                        "year": 2025,
                                        "url": "https://en.wikipedia.org/wiki/2025_Formula_One_World_Championship",
                                    },
                                ],
                                "main_colours": ["White"],
                            },
                        ],
                    },
                },
            },
        ],
    )
    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "rules" / "raw" / "a.json",
        [{"rule": "X"}],
    )
    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "points" / "raw" / "a.json",
        [{"points": "X"}],
    )

    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "season"
        / "raw"
        / "f1_tyre_manufacturers_by_season.json",
        [{"seasons": [1950], "manufacturers": ["Pirelli"]}],
    )

    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "seasons" / "raw" / "a.json",
        [{"season": 2026}, {"season": 1950}, {"season": 2005}],
    )

    merge_layer_zero_raw_outputs(base_wiki_dir)

    circuits_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "circuits" / "circuits.json").read_text(
            encoding="utf-8",
        ),
    )
    constructors_merged = json.loads(
        (
            base_wiki_dir / "layers" / "0_layer" / "constructors" / "constructors.json"
        ).read_text(
            encoding="utf-8",
        ),
    )
    drivers_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "drivers" / "drivers.json").read_text(
            encoding="utf-8",
        ),
    )
    races_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "races" / "races.json").read_text(
            encoding="utf-8",
        ),
    )
    engines_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "engines" / "engines.json").read_text(
            encoding="utf-8",
        ),
    )
    grands_prix_merged = json.loads(
        (
            base_wiki_dir / "layers" / "0_layer" / "grands_prix" / "grands_prix.json"
        ).read_text(encoding="utf-8"),
    )
    teams_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "teams" / "teams.json").read_text(
            encoding="utf-8",
        ),
    )
    seasons_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "seasons" / "seasons.json").read_text(
            encoding="utf-8",
        ),
    )
    season_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "season" / "season.json").read_text(
            encoding="utf-8",
        ),
    )

    assert circuits_merged == [
        {
            "circuit": "Monza",
            "racing_series": {
                "formula_one": {
                    "turns": 11,
                    "circuit_status": "active",
                    "grands_prix": ["Italian Grand Prix"],
                },
            },
        },
    ]
    assert constructors_merged == [
        {
            "constructor": "Ferrari",
            "racing_series": {
                "formula_one": {
                    "engine": "Ferrari",
                    "licensed_in": "Italy",
                    "wins": 248,
                    "status": "active",
                },
            },
        },
        {
            "constructor": {"text": "Indy Team", "url": "https://example.com/indy"},
            "racing_series": {
                "AAA_national_championship": [],
                "formula_one": {
                    "status": "former",
                    "indianapolis_only": True,
                },
            },
        },
        {
            "constructor": "McLaren",
            "racing_series": {
                "formula_one": {
                    "wins": 2,
                    "status": "active",
                },
            },
        },
        {
            "constructor": {"text": "Team Old", "url": "https://example.com/old"},
            "racing_series": {
                "formula_one": {
                    "wins": 0,
                    "status": "former",
                },
            },
        },
    ]

    female_driver = next(item for item in drivers_merged if item["driver"]["text"] == "Maria")
    assert female_driver == {
        "driver": {"text": "Maria", "url": "https://example.com/maria"},
        "gender": "female",
        "racing_series": {"formula_one": {}},
    }
    female_driver = next(
        item for item in drivers_merged if item["driver"]["text"] == "Maria"
    )
    assert female_driver["gender"] == "female"

    ordered_driver_names = [item["driver"]["text"] for item in drivers_merged]
    assert ordered_driver_names.index("Lewis Hamilton") < ordered_driver_names.index(
        "Max Verstappen",
    )

    fatality_driver = next(
        item for item in drivers_merged if item["driver"]["text"] == "X"
    )
    assert fatality_driver["death"] == {
        "date": "2000-01-01",
        "age": 28,
        "crash": {
            "event": "test",
            "circuit": "Monza",
            "car": "Car",
            "session": "Practice",
        },
    }

    amati_driver = next(
        item
        for item in drivers_merged
        if item["driver"]["url"] == "https://en.wikipedia.org/wiki/Giovanna_Amati"
    )
    assert amati_driver["race_entries"] == 3
    assert "race_starts" not in amati_driver
    assert amati_driver["nationality"] == "Italy"
    assert "entries" not in amati_driver
    assert amati_driver["teams"] == [
        {"text": "Brabham", "url": "https://en.wikipedia.org/wiki/Brabham"},
    ]

    bob_anderson = next(
        item
        for item in drivers_merged
        if item["driver"]["url"]
        == "https://en.wikipedia.org/wiki/Bob_Anderson_(racing_driver)"
    )
    assert bob_anderson["death"]["date"] == "1967-08-14"
    assert bob_anderson["race_entries"] == 29

    world_race = next(item for item in races_merged if "grand_prix" in item)
    assert world_race["championship"] is True
    assert world_race["red_flag"] == {
        "lap": 64,
        "winner": "Stewart",
        "failed_to_make_restart": {"drivers": ["A"], "reason": "Crash"},
    }
    assert "lap" not in world_race
    assert "winner" not in world_race
    assert "failed_to_make_restart" not in world_race

    non_champ_race = next(item for item in races_merged if "event" in item)
    assert non_champ_race["championship"] is False
    assert non_champ_race["red_flag"] == {"lap": 15, "incident": "Crash"}
    assert "lap" not in non_champ_race
    assert "incident" not in non_champ_race

    assert engines_merged == [
        {
            "manufacturer": "Ferrari",
            "racing_series": {
                "formula_one": {
                    "manufacturer_status": "active",
                    "wins": 200,
                },
            },
        },
        {
            "manufacturer": "Offy",
            "racing_series": {
                "AAA_national_championship": [],
                "formula_one": {
                    "status": "former",
                    "indianapolis_only": True,
                },
            },
        },
    ]

    assert grands_prix_merged == [
        {
            "grand_prix": "Italian",
            "racing_series": {
                "formula_one": {
                    "race_status": "active",
                    "total": 74,
                },
            },
        },
    ]

    ferrari_team = next(item for item in teams_merged if item["team"] == "Ferrari")
    assert ferrari_team["racing_series"] == {
        "formula_one": {
            "liveries": ["Marlboro"],
        },
    }

    rob_walker_team = next(
        item for item in teams_merged if item["team"] == "Rob Walker"
    )
    assert rob_walker_team["racing_series"] == {
        "formula_one": {
            "seasons": ["1950"],
            "privateer": True,
        },
    }


    team_x = next(item for item in teams_merged if isinstance(item.get("team"), dict) and item["team"]["text"] == "Team X")
    assert team_x["team"] == {"text": "Team X", "url": "https://example.com/team-x"}
    team_x = next(
        item
        for item in teams_merged
        if isinstance(item.get("team"), dict) and item["team"]["text"] == "Team X"
    )
    assert team_x["racing_series"] == {
        "formula_one": {
            "constructor": {"text": "Team X", "url": "https://example.com/team-x"},
            "engine": {"text": "Engine X", "url": "https://example.com/engine-x"},
            "wins": 1,
        },
    }

    cadillac_team = next(
        item
        for item in teams_merged
        if isinstance(item.get("team"), dict)
        and item["team"]["text"] == "Cadillac"
    )
    assert cadillac_team["racing_series"] == {
        "formula_one": {
            "constructor": {
                "text": "Cadillac",
                "url": "https://en.wikipedia.org/wiki/Cadillac_in_Formula_One",
            },
            "engine": [
                {
                    "text": "Ferrari",
                    "url": "https://en.wikipedia.org/wiki/Scuderia_Ferrari",
                },
            ],
            "wins": 0,
            "liveries": [{"main_colours": ["White", "Black"]}],
        },
    }

    audi_team = next(item for item in teams_merged if _team_text(item) == "Audi")
    assert audi_team["team"] == {
        "text": "Audi",
        "url": "https://en.wikipedia.org/wiki/Audi_in_Formula_One",
    }
    assert audi_team["racing_series"] == {
        "formula_one": {
            "wins": 0,
            "liveries": [{"main_colours": ["Silver", "Red", "Black"]}],
        },
    }

    racing_bulls = next(item for item in teams_merged if _team_text(item) == "Racing Bulls")
    assert racing_bulls["racing_series"] == {
        "formula_one": {
            "seasons": [
                {
                    "year": 2024,
                    "url": "https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship",
                    "livery": {
                        "main_colours": ["Blue", "White"],
                        "special_liveries": "Miami",
                    },
                },
                {
                    "year": 2025,
                    "url": "https://en.wikipedia.org/wiki/2025_Formula_One_World_Championship",
                    "livery": {
                        "main_colours": ["White"],
                    },
                },
            ],
            "wins": 0,
        },
    }

    assert seasons_merged == [{"season": 1950}, {"season": 2005}, {"season": 2026}]

    assert season_merged == [{"season": 1950, "tyre_manufacturers": ["Pirelli"]}]

    assert not (base_wiki_dir / "layers" / "0_layer" / "rules" / "rules.json").exists()
    assert not (
        base_wiki_dir / "layers" / "0_layer" / "points" / "points.json"
    ).exists()
