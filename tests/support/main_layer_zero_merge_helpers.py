from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path



def _team_text(record: dict[str, object]) -> str:
    team = record.get("team")
    if isinstance(team, dict):
        value = team.get("text")
        return value if isinstance(value, str) else ""
    return team if isinstance(team, str) else ""


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _seed_domain_raw(
    base_wiki_dir: Path,
    domain: str,
    files_payloads: list[tuple[str, object]],
) -> None:
    for filename, payload in files_payloads:
        _write_json(
            base_wiki_dir / "layers" / "0_layer" / domain / "raw" / filename,
            payload,
        )


def _circuits_raw_payloads() -> list[tuple[str, object]]:
    return [
        (
            "a.json",
            [
                {
                    "circuit": "Monza",
                    "turns": 11,
                    "circuit_status": "active",
                    "grands_prix": ["Italian Grand Prix"],
                },
            ],
        ),
    ]


def _constructors_raw_payloads() -> list[tuple[str, object]]:
    return [
        (
            "a.json",
            [
                {
                    "constructor": "Ferrari",
                    "licensed_in": "Italy",
                    "engine": "Ferrari",
                    "wins": 248,
                },
            ],
        ),
        ("f1_constructor_standings.json", [{"constructor": "McLaren", "wins": 2}]),
        (
            "f1_former_constructors.json",
            [
                {
                    "constructor": {
                        "text": "Team Old",
                        "url": "https://example.com/old",
                    },
                    "wins": 0,
                },
            ],
        ),
        (
            "f1_indianapolis_only_constructors.json",
            [
                {
                    "constructor": "Indy Team",
                    "constructor_url": "https://example.com/indy",
                },
            ],
        ),
    ]


GIOVANNA_AMATI_URL = "https://en.wikipedia.org/wiki/Giovanna_Amati"
BOB_ANDERSON_URL = "https://en.wikipedia.org/wiki/Bob_Anderson_(racing_driver)"
AMATI_RACE_ENTRIES = 3
BOB_ANDERSON_RACE_ENTRIES = 29


def _drivers_raw_payloads() -> list[tuple[str, object]]:
    return [
        (
            "female_drivers.json",
            [{"driver": {"text": "Maria", "url": "https://example.com/maria"}}],
        ),
        (
            "drivers.json",
            [
                {
                    "driver": {
                        "text": "Max Verstappen",
                        "url": "https://example.com/max",
                    },
                },
                {
                    "driver": {
                        "text": "Lewis Hamilton",
                        "url": "https://example.com/lewis",
                    },
                },
                {
                    "driver": {
                        "text": "Giovanna Amati",
                        "url": GIOVANNA_AMATI_URL,
                    },
                    "race_entries": AMATI_RACE_ENTRIES,
                    "nationality": "Italy",
                },
            ],
        ),
        (
            "f1_women_drivers_who_entered_a_formula_one_race.json",
            [
                {
                    "driver": {
                        "text": "Giovanna Amati",
                        "url": GIOVANNA_AMATI_URL,
                    },
                    "entries": AMATI_RACE_ENTRIES,
                    "teams": [
                        {
                            "text": "Brabham",
                            "url": "https://en.wikipedia.org/wiki/Brabham",
                        },
                    ],
                },
                {
                    "driver": {
                        "text": "Bob Anderson",
                        "url": BOB_ANDERSON_URL,
                    },
                    "is_active": False,
                    "race_entries": BOB_ANDERSON_RACE_ENTRIES,
                },
            ],
        ),
        (
            "f1_driver_fatalities.json",
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
                        "url": BOB_ANDERSON_URL,
                    },
                    "date": "1967-08-14",
                    "age": 36,
                    "event": "Test",
                    "circuit": "Silverstone",
                    "car": "Brabham BT11",
                    "session": "Test",
                },
            ],
        ),
    ]


def _races_raw_payloads() -> list[tuple[str, object]]:
    return [
        (
            "f1_red_flagged_world_championship_races.json",
            [
                {
                    "season": 1971,
                    "grand_prix": "Canadian",
                    "lap": 64,
                    "winner": "Stewart",
                    "failed_to_make_restart": {"drivers": ["A"], "reason": "Crash"},
                },
            ],
        ),
        (
            "f1_red_flagged_non_championship_races.json",
            [
                {
                    "season": 1971,
                    "event": "Victory Race",
                    "lap": 15,
                    "incident": "Crash",
                },
            ],
        ),
    ]


def _engines_raw_payloads() -> list[tuple[str, object]]:
    return [
        (
            "f1_engine_manufacturers.json",
            [
                {
                    "manufacturer": "Ferrari",
                    "manufacturer_status": "active",
                    "wins": 200,
                },
            ],
        ),
        (
            "f1_indianapolis_only_engine_manufacturers.json",
            [{"manufacturer": "Offy"}],
        ),
    ]


def _grands_prix_raw_payloads() -> list[tuple[str, object]]:
    return [
        (
            "a.json",
            [{"grand_prix": "Italian", "race_status": "active", "total": 74}],
        ),
    ]


def _teams_raw_payloads() -> list[tuple[str, object]]:
    return [
        (
            "f1_sponsorship_liveries.json",
            [{"team": "Ferrari", "liveries": ["Marlboro"]}],
        ),
        ("f1_privateer_teams.json", [{"team": "Rob Walker", "seasons": ["1950"]}]),
        (
            "f1_constructors_2026.json",
            [
                {
                    "constructor": {
                        "text": "Team X",
                        "url": "https://example.com/team-x",
                    },
                    "engine": {
                        "text": "Engine X",
                        "url": "https://example.com/engine-x",
                    },
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
        ),
        (
            "cadillac_livery.json",
            [
                {
                    "team": {
                        "text": "Cadillac",
                        "url": "https://en.wikipedia.org/wiki/Cadillac_in_Formula_One",
                    },
                    "racing_series": {
                        "formula_one": {
                            "liveries": [{"main_colours": ["White", "Black"]}],
                        },
                    },
                },
            ],
        ),
        (
            "audi_constructor.json",
            [
                {
                    "team": {
                        "text": "Audi",
                        "url": "https://en.wikipedia.org/wiki/Audi_in_Formula_One",
                    },
                    "racing_series": {"formula_one": {"wins": 0}},
                },
            ],
        ),
        (
            "audi_livery.json",
            [
                {
                    "team": "Audi",
                    "racing_series": {
                        "formula_one": {
                            "liveries": [
                                {"main_colours": ["Silver", "Red", "Black"]},
                            ],
                        },
                    },
                },
            ],
        ),
        (
            "racing_bulls_constructor.json",
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
        ),
        (
            "racing_bulls_livery.json",
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
                                {
                                    "season": [
                                        {
                                            "year": 2024,
                                            "url": "https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship",
                                        },
                                    ],
                                    "main_colours": ["Red"],
                                },
                            ],
                        },
                    },
                },
            ],
        ),
        (
            "aston_martin_constructor.json",
            [
                {
                    "team": {
                        "text": "Aston Martin",
                        "url": "https://en.wikipedia.org/wiki/Aston_Martin_in_Formula_One",
                    },
                    "racing_series": {
                        "formula_one": {
                            "seasons": [
                                {
                                    "year": 1959,
                                    "url": "https://en.wikipedia.org/wiki/1959_Formula_One_World_Championship",
                                },
                                {
                                    "year": 1960,
                                    "url": "https://en.wikipedia.org/wiki/1960_Formula_One_World_Championship",
                                },
                            ],
                        },
                    },
                },
            ],
        ),
        (
            "aston_martin_livery.json",
            [
                {
                    "team": {
                        "text": "Aston Martin",
                        "url": "https://en.wikipedia.org/wiki/Aston_Martin_in_Formula_One",
                    },
                    "racing_series": {
                        "formula_one": {
                            "liveries": [
                                {
                                    "season": [
                                        {
                                            "year": 1959,
                                            "url": "https://en.wikipedia.org/wiki/1959_Formula_One_World_Championship",
                                        },
                                        {
                                            "year": 1960,
                                            "url": "https://en.wikipedia.org/wiki/1960_Formula_One_World_Championship",
                                        },
                                    ],
                                    "main_colours": ["British racing green"],
                                },
                            ],
                        },
                    },
                },
            ],
        ),
    ]


def _season_raw_payloads() -> list[tuple[str, object]]:
    return [
        (
            "f1_tyre_manufacturers_by_season.json",
            [{"seasons": [1950], "manufacturers": ["Pirelli"]}],
        ),
    ]


def _seasons_raw_payloads() -> list[tuple[str, object]]:
    return [("a.json", [{"season": 2026}, {"season": 1950}, {"season": 2005}])]


def _layer_zero_seed_data() -> tuple[tuple[str, list[tuple[str, object]]], ...]:
    return (
        ("circuits", _circuits_raw_payloads()),
        ("constructors", _constructors_raw_payloads()),
        ("drivers", _drivers_raw_payloads()),
        ("races", _races_raw_payloads()),
        ("engines", _engines_raw_payloads()),
        ("grands_prix", _grands_prix_raw_payloads()),
        ("teams", _teams_raw_payloads()),
        ("rules", [("a.json", [{"rule": "X"}])]),
        ("points", [("a.json", [{"points": "X"}])]),
        ("season", _season_raw_payloads()),
        ("seasons", _seasons_raw_payloads()),
    )


def _seed_layer_zero_raw_data(base_wiki_dir: Path) -> None:
    for domain, files_payloads in _layer_zero_seed_data():
        _seed_domain_raw(base_wiki_dir, domain, files_payloads)


def _driver_record_by_name(
    drivers_merged: list[dict[str, object]],
    driver_name: str,
) -> dict[str, object]:
    return next(
        item for item in drivers_merged if item["driver"]["text"] == driver_name
    )


def _driver_record_by_url(
    drivers_merged: list[dict[str, object]],
    driver_url: str,
) -> dict[str, object]:
    return next(
        item for item in drivers_merged if item["driver"]["url"] == driver_url
    )


def _team_record_by_name(
    teams_merged: list[dict[str, object]],
    team_name: str,
) -> dict[str, object]:
    return next(item for item in teams_merged if _team_text(item) == team_name)


def _assert_circuits_output(circuits_merged: list[dict[str, object]]) -> None:
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


def _assert_constructors_output(constructors_merged: list[dict[str, object]]) -> None:
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


def _assert_drivers_output(drivers_merged: list[dict[str, object]]) -> None:
    female_driver = _driver_record_by_name(drivers_merged, "Maria")
    assert female_driver == {
        "driver": {"text": "Maria", "url": "https://example.com/maria"},
        "gender": "female",
        "racing_series": {"formula_one": {}},
    }
    assert female_driver["gender"] == "female"

    ordered_driver_names = [item["driver"]["text"] for item in drivers_merged]
    assert ordered_driver_names.index("Lewis Hamilton") < ordered_driver_names.index(
        "Max Verstappen",
    )

    fatality_driver = _driver_record_by_name(drivers_merged, "X")
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

    amati_driver = _driver_record_by_url(
        drivers_merged,
        GIOVANNA_AMATI_URL,
    )
    assert amati_driver["race_entries"] == AMATI_RACE_ENTRIES
    assert "race_starts" not in amati_driver
    assert amati_driver["nationality"] == "Italy"
    assert "entries" not in amati_driver
    assert amati_driver["teams"] == [
        {"text": "Brabham", "url": "https://en.wikipedia.org/wiki/Brabham"},
    ]

    bob_anderson = _driver_record_by_url(
        drivers_merged,
        BOB_ANDERSON_URL,
    )
    assert bob_anderson["death"]["date"] == "1967-08-14"
    assert bob_anderson["race_entries"] == BOB_ANDERSON_RACE_ENTRIES


def _assert_races_output(races_merged: list[dict[str, object]]) -> None:
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


def _assert_engines_output(engines_merged: list[dict[str, object]]) -> None:
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


def _assert_grands_prix_output(grands_prix_merged: list[dict[str, object]]) -> None:
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


def _assert_teams_output(teams_merged: list[dict[str, object]]) -> None:
    ferrari_team = _team_record_by_name(teams_merged, "Ferrari")
    assert ferrari_team["racing_series"] == {
        "formula_one": {
            "liveries": ["Marlboro"],
        },
    }

    rob_walker_team = _team_record_by_name(teams_merged, "Rob Walker")
    assert rob_walker_team["racing_series"] == {
        "formula_one": {
            "seasons": ["1950"],
            "privateer": True,
        },
    }

    team_x = _team_record_by_name(teams_merged, "Team X")
    assert team_x["team"] == {"text": "Team X", "url": "https://example.com/team-x"}
    assert team_x["racing_series"] == {
        "formula_one": {
            "constructor": {"text": "Team X", "url": "https://example.com/team-x"},
            "engine": {"text": "Engine X", "url": "https://example.com/engine-x"},
            "wins": 1,
        },
    }

    cadillac_team = _team_record_by_name(teams_merged, "Cadillac")
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

    audi_team = _team_record_by_name(teams_merged, "Audi")
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

    racing_bulls = _team_record_by_name(teams_merged, "Racing Bulls")
    assert racing_bulls["racing_series"] == {
        "formula_one": {
            "seasons": [
                {
                    "year": 2024,
                    "url": "https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship",
                    "liveries": [
                        {
                            "main_colours": ["Blue", "White"],
                            "special_liveries": "Miami",
                        },
                        {
                            "main_colours": ["Red"],
                        },
                    ],
                },
                {
                    "year": 2025,
                    "url": "https://en.wikipedia.org/wiki/2025_Formula_One_World_Championship",
                    "liveries": [
                        {
                            "main_colours": ["White"],
                        },
                    ],
                },
            ],
            "wins": 0,
        },
    }

    aston_martin = _team_record_by_name(teams_merged, "Aston Martin")
    assert aston_martin["racing_series"] == {
        "formula_one": {
            "seasons": [
                {
                    "year": 1959,
                    "url": "https://en.wikipedia.org/wiki/1959_Formula_One_World_Championship",
                    "liveries": [{"main_colours": ["British racing green"]}],
                },
                {
                    "year": 1960,
                    "url": "https://en.wikipedia.org/wiki/1960_Formula_One_World_Championship",
                    "liveries": [{"main_colours": ["British racing green"]}],
                },
            ],
        },
    }


def _assert_seasons_outputs(
    seasons_merged: list[dict[str, object]],
    season_merged: list[dict[str, object]],
) -> None:
    assert seasons_merged == [{"season": 1950}, {"season": 2005}, {"season": 2026}]
    assert season_merged == [{"season": 1950, "tyre_manufacturers": ["Pirelli"]}]


def _assert_missing_outputs(base_wiki_dir: Path) -> None:
    assert not (base_wiki_dir / "layers" / "0_layer" / "rules" / "rules.json").exists()
    assert not (
        base_wiki_dir / "layers" / "0_layer" / "points" / "points.json"
    ).exists()


def _assert_merged_outputs(
    *,
    circuits_merged: list[dict[str, object]],
    constructors_merged: list[dict[str, object]],
    drivers_merged: list[dict[str, object]],
    races_merged: list[dict[str, object]],
    engines_merged: list[dict[str, object]],
    grands_prix_merged: list[dict[str, object]],
    teams_merged: list[dict[str, object]],
    seasons_merged: list[dict[str, object]],
    season_merged: list[dict[str, object]],
    base_wiki_dir: Path,
) -> None:
    _assert_circuits_output(circuits_merged)
    _assert_constructors_output(constructors_merged)
    _assert_drivers_output(drivers_merged)
    _assert_races_output(races_merged)
    _assert_engines_output(engines_merged)
    _assert_grands_prix_output(grands_prix_merged)
    _assert_teams_output(teams_merged)
    _assert_seasons_outputs(seasons_merged, season_merged)
    _assert_missing_outputs(base_wiki_dir)
