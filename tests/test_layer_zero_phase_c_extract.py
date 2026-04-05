# ruff: noqa: PLR2004
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from layers.zero.extract import extract_layer_zero_phase_c

if TYPE_CHECKING:
    from pathlib import Path


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _b_merge_path(base: Path, domain: str) -> Path:
    return base / "layers" / "0_layer" / domain / "B_merge"


def _c_extract_path(base: Path, domain: str) -> Path:
    return base / "layers" / "0_layer" / domain / "C_extract"


class TestCopiesBMergeFiles:
    def test_copies_b_merge_files_to_c_extract(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [{"circuit": {"text": "Monza"}}]
        _write_json(_b_merge_path(base, "circuits") / "circuits.json", payload)

        extract_layer_zero_phase_c(base)

        copied = _c_extract_path(base, "circuits") / "circuits.json"
        assert copied.exists()
        assert json.loads(copied.read_text(encoding="utf-8")) == payload

    def test_does_nothing_if_layer_zero_dir_missing(self, tmp_path: Path) -> None:
        extract_layer_zero_phase_c(tmp_path / "nonexistent")

    def test_skips_domain_without_b_merge(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        (base / "layers" / "0_layer" / "circuits").mkdir(parents=True)

        extract_layer_zero_phase_c(base)

        assert not _c_extract_path(base, "circuits").exists()


class TestExtractFromChassisConstructors:
    def test_extracts_licensed_in_to_countries(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {
                "constructor": {"text": "Team A"},
                "licensed_in": [
                    {"text": "France", "url": "https://en.wikipedia.org/wiki/France"},
                    {"text": "Italy", "url": "https://en.wikipedia.org/wiki/Italy"},
                ],
            },
        ]
        _write_json(
            _b_merge_path(base, "chassis_constructors") / "chassis_constructors.json",
            payload,
        )

        extract_layer_zero_phase_c(base)

        countries_file = (
            _c_extract_path(base, "countries") / "from_chassis_constructors.json"
        )
        assert countries_file.exists()
        countries = json.loads(countries_file.read_text(encoding="utf-8"))
        assert len(countries) == 2
        france = {"text": "France", "url": "https://en.wikipedia.org/wiki/France"}
        italy = {"text": "Italy", "url": "https://en.wikipedia.org/wiki/Italy"}
        assert france in countries
        assert italy in countries

    def test_handles_single_licensed_in_value(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        germany = {"text": "Germany", "url": "https://en.wikipedia.org/wiki/Germany"}
        payload = [
            {
                "constructor": {"text": "Team B"},
                "licensed_in": germany,
            },
        ]
        _write_json(
            _b_merge_path(base, "chassis_constructors") / "chassis_constructors.json",
            payload,
        )

        extract_layer_zero_phase_c(base)

        countries_file = (
            _c_extract_path(base, "countries") / "from_chassis_constructors.json"
        )
        countries = json.loads(countries_file.read_text(encoding="utf-8"))
        assert len(countries) == 1
        assert germany in countries


class TestExtractFromCircuits:
    def test_extracts_country_to_countries_and_location_to_locations(
        self,
        tmp_path: Path,
    ) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {
                "circuit": {"text": "Monza"},
                "country": {
                    "text": "Italy",
                    "url": "https://en.wikipedia.org/wiki/Italy",
                },
                "location": {
                    "text": "Monza",
                    "url": "https://en.wikipedia.org/wiki/Monza",
                },
            },
            {
                "circuit": {"text": "Silverstone"},
                "country": {
                    "text": "United Kingdom",
                    "url": "https://en.wikipedia.org/wiki/United_Kingdom",
                },
                "location": {
                    "text": "Silverstone",
                    "url": "https://en.wikipedia.org/wiki/Silverstone",
                },
            },
        ]
        _write_json(_b_merge_path(base, "circuits") / "circuits.json", payload)

        extract_layer_zero_phase_c(base)

        countries_file = _c_extract_path(base, "countries") / "from_circuits.json"
        assert countries_file.exists()
        countries = json.loads(countries_file.read_text(encoding="utf-8"))
        assert len(countries) == 2

        locations_file = _c_extract_path(base, "locations") / "from_circuits.json"
        assert locations_file.exists()
        locations = json.loads(locations_file.read_text(encoding="utf-8"))
        assert len(locations) == 2
        monza = {"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}
        assert monza in locations


class TestExtractFromConstructors:
    def test_extracts_engine_teams_countries(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {
                "constructor": {"text": "Alpine"},
                "engine": [
                    {
                        "text": "Mercedes",
                        "url": "https://en.wikipedia.org/wiki/Mercedes",
                    },
                ],
                "racing_series": {
                    "formula_one": {
                        "antecedent_teams": [
                            {
                                "text": "Toleman",
                                "url": "https://en.wikipedia.org/wiki/Toleman",
                            },
                        ],
                        "based_in": [
                            {
                                "text": "United Kingdom",
                                "url": "https://en.wikipedia.org/wiki/United_Kingdom",
                            },
                        ],
                        "licensed_in": {
                            "text": "France",
                            "url": "https://en.wikipedia.org/wiki/France",
                        },
                    },
                },
            },
        ]
        _write_json(
            _b_merge_path(base, "constructors") / "constructors.json",
            payload,
        )

        extract_layer_zero_phase_c(base)

        engines_file = _c_extract_path(base, "engines") / "from_constructors.json"
        assert engines_file.exists()
        engines = json.loads(engines_file.read_text(encoding="utf-8"))
        assert len(engines) == 1
        mercedes = {"text": "Mercedes", "url": "https://en.wikipedia.org/wiki/Mercedes"}
        assert mercedes in engines

        teams_file = _c_extract_path(base, "teams") / "from_constructors.json"
        assert teams_file.exists()
        teams = json.loads(teams_file.read_text(encoding="utf-8"))
        assert len(teams) == 1
        toleman = {"text": "Toleman", "url": "https://en.wikipedia.org/wiki/Toleman"}
        assert toleman in teams

        countries_file = _c_extract_path(base, "countries") / "from_constructors.json"
        assert countries_file.exists()
        countries = json.loads(countries_file.read_text(encoding="utf-8"))
        assert len(countries) == 2
        france = {"text": "France", "url": "https://en.wikipedia.org/wiki/France"}
        assert france in countries
        assert {
            "text": "United Kingdom",
            "url": "https://en.wikipedia.org/wiki/United_Kingdom",
        } in countries


class TestExtractFromDrivers:
    def test_extracts_nationality_to_countries(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {"driver": {"text": "Ayrton Senna"}, "nationality": "Brazil"},
            {"driver": {"text": "Michael Schumacher"}, "nationality": "Germany"},
        ]
        _write_json(_b_merge_path(base, "drivers") / "drivers.json", payload)

        extract_layer_zero_phase_c(base)

        countries_file = _c_extract_path(base, "countries") / "from_drivers.json"
        assert countries_file.exists()
        countries = json.loads(countries_file.read_text(encoding="utf-8"))
        assert "Brazil" in countries
        assert "Germany" in countries

    def test_skips_records_without_nationality(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [{"driver": {"text": "Unknown"}}]
        _write_json(_b_merge_path(base, "drivers") / "drivers.json", payload)

        extract_layer_zero_phase_c(base)

        countries_file = _c_extract_path(base, "countries") / "from_drivers.json"
        assert not countries_file.exists()


class TestExtractFromEngines:
    def test_extracts_engines_built_in_to_countries(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {
                "manufacturer": {"text": "Ferrari"},
                "racing_series": {
                    "formula_one": {
                        "engines_built_in": [
                            {
                                "text": "Italy",
                                "url": "https://en.wikipedia.org/wiki/Italy",
                            },
                        ],
                    },
                },
            },
        ]
        _write_json(_b_merge_path(base, "engines") / "engines.json", payload)

        extract_layer_zero_phase_c(base)

        countries_file = _c_extract_path(base, "countries") / "from_engines.json"
        assert countries_file.exists()
        countries = json.loads(countries_file.read_text(encoding="utf-8"))
        assert len(countries) == 1
        italy = {"text": "Italy", "url": "https://en.wikipedia.org/wiki/Italy"}
        assert italy in countries


class TestExtractFromRaces:
    def test_extracts_winner_and_failed_to_make_restart_drivers(
        self,
        tmp_path: Path,
    ) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {
                "season": 1973,
                "red_flag": {
                    "winner": {
                        "text": "Peter Revson",
                        "url": "https://en.wikipedia.org/wiki/Peter_Revson",
                    },
                    "failed_to_make_restart": [
                        {
                            "drivers": [
                                {
                                    "text": "Jody Scheckter",
                                    "url": "https://en.wikipedia.org/wiki/Jody_Scheckter",
                                },
                            ],
                            "reason": "Crash",
                        },
                    ],
                },
            },
        ]
        _write_json(_b_merge_path(base, "races") / "races.json", payload)

        extract_layer_zero_phase_c(base)

        drivers_file = _c_extract_path(base, "drivers") / "from_races.json"
        assert drivers_file.exists()
        drivers = json.loads(drivers_file.read_text(encoding="utf-8"))
        driver_texts = [d["text"] for d in drivers if isinstance(d, dict)]
        assert "Peter Revson" in driver_texts
        assert "Jody Scheckter" in driver_texts

    def test_skips_null_failed_to_make_restart(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {
                "season": 1971,
                "red_flag": {
                    "winner": {
                        "text": "Jackie Stewart",
                        "url": "https://example.com/js",
                    },
                    "failed_to_make_restart": None,
                },
            },
        ]
        _write_json(_b_merge_path(base, "races") / "races.json", payload)

        extract_layer_zero_phase_c(base)

        drivers_file = _c_extract_path(base, "drivers") / "from_races.json"
        assert drivers_file.exists()
        drivers = json.loads(drivers_file.read_text(encoding="utf-8"))
        assert len(drivers) == 1
        assert drivers[0]["text"] == "Jackie Stewart"


class TestCrossDomainFromFilesNormalization:
    def test_from_files_are_sorted_and_deduplicated(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {"driver": {"text": "Driver A"}, "nationality": "Brazil"},
            {"driver": {"text": "Driver B"}, "nationality": "Argentina"},
            {"driver": {"text": "Driver C"}, "nationality": "Brazil"},
        ]
        _write_json(_b_merge_path(base, "drivers") / "drivers.json", payload)

        extract_layer_zero_phase_c(base)

        countries_file = _c_extract_path(base, "countries") / "from_drivers.json"
        countries = json.loads(countries_file.read_text(encoding="utf-8"))
        assert countries == ["Argentina", "Brazil"]

    def test_from_files_are_sorted_and_deduplicated_for_objects(
        self,
        tmp_path: Path,
    ) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {
                "season": 1971,
                "red_flag": {
                    "winner": {
                        "url": "https://example.com/js",
                        "text": "Jackie Stewart",
                    },
                    "failed_to_make_restart": [
                        {
                            "reason": "Crash",
                            "drivers": [
                                {
                                    "text": "Clay Regazzoni",
                                    "url": "https://example.com/cr",
                                },
                            ],
                        },
                        {
                            "reason": "Crash",
                            "drivers": [
                                {
                                    "url": "https://example.com/cr",
                                    "text": "Clay Regazzoni",
                                },
                            ],
                        },
                    ],
                },
            },
        ]
        _write_json(_b_merge_path(base, "races") / "races.json", payload)

        extract_layer_zero_phase_c(base)

        drivers_file = _c_extract_path(base, "drivers") / "from_races.json"
        drivers = json.loads(drivers_file.read_text(encoding="utf-8"))
        assert drivers == [
            {"text": "Clay Regazzoni", "url": "https://example.com/cr"},
            {"text": "Jackie Stewart", "url": "https://example.com/js"},
        ]


class TestExtractFromSeasons:
    def test_extracts_tyre_manufacturers_and_constructors_champion(
        self,
        tmp_path: Path,
    ) -> None:
        base = tmp_path / "data" / "wiki"
        pirelli = {"text": "Pirelli", "url": "https://en.wikipedia.org/wiki/Pirelli"}
        dunlop = {
            "text": "Dunlop",
            "url": "https://en.wikipedia.org/wiki/Dunlop_Rubber",
        }
        vanwall = {"text": "Vanwall", "url": "https://en.wikipedia.org/wiki/Vanwall"}
        payload = [
            {
                "season": {"year": 1958},
                "tyre_manufacturers": [pirelli, dunlop],
                "constructors_champion": [vanwall],
            },
        ]
        _write_json(_b_merge_path(base, "seasons") / "seasons.json", payload)

        extract_layer_zero_phase_c(base)

        tyre_file = _c_extract_path(base, "tyre_manufacturers") / "from_seasons.json"
        assert tyre_file.exists()
        tyres = json.loads(tyre_file.read_text(encoding="utf-8"))
        assert pirelli in tyres
        assert dunlop in tyres

        constructors_file = _c_extract_path(base, "constructors") / "from_seasons.json"
        assert constructors_file.exists()
        constructors = json.loads(constructors_file.read_text(encoding="utf-8"))
        assert vanwall in constructors

    def test_handles_single_tyre_manufacturer(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        goodyear = {
            "text": "Goodyear",
            "url": "https://en.wikipedia.org/wiki/Goodyear_Tire_and_Rubber_Company",
        }
        payload = [{"season": {"year": 1975}, "tyre_manufacturers": goodyear}]
        _write_json(_b_merge_path(base, "seasons") / "seasons.json", payload)

        extract_layer_zero_phase_c(base)

        tyre_file = _c_extract_path(base, "tyre_manufacturers") / "from_seasons.json"
        tyres = json.loads(tyre_file.read_text(encoding="utf-8"))
        assert len(tyres) == 1
        assert goodyear in tyres

    def test_skips_records_without_tyre_or_champion(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [{"season": {"year": 1950}}]
        _write_json(_b_merge_path(base, "seasons") / "seasons.json", payload)

        extract_layer_zero_phase_c(base)

        assert not (
            _c_extract_path(base, "tyre_manufacturers") / "from_seasons.json"
        ).exists()
        assert not (
            _c_extract_path(base, "constructors") / "from_seasons.json"
        ).exists()


class TestExtractFromTeams:
    def test_extracts_colors_sponsors_teams_countries(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        toleman = {"text": "Toleman", "url": "https://en.wikipedia.org/wiki/Toleman"}
        uk = {
            "text": "United Kingdom",
            "url": "https://en.wikipedia.org/wiki/United_Kingdom",
        }
        france = {"text": "France", "url": "https://en.wikipedia.org/wiki/France"}
        elf = {"text": "Elf", "url": "https://en.wikipedia.org/wiki/Elf_Aquitaine"}
        payload = [
            {
                "team": "Benetton",
                "racing_series": {
                    "formula_one": {
                        "antecedent_teams": [toleman],
                        "based_in": [uk],
                        "licensed_in": france,
                        "liveries": [
                            {
                                "season": [{"year": 1986}],
                                "main_colours": ["White", "Blue"],
                                "additional_colours": ["Red"],
                                "main_sponsors": ["None"],
                                "additional_major_sponsors": [elf],
                            },
                        ],
                    },
                },
            },
        ]
        _write_json(_b_merge_path(base, "teams") / "teams.json", payload)

        extract_layer_zero_phase_c(base)

        colors_file = _c_extract_path(base, "colors") / "from_teams.json"
        assert colors_file.exists()
        colors = json.loads(colors_file.read_text(encoding="utf-8"))
        assert "White" in colors
        assert "Blue" in colors
        assert "Red" in colors

        sponsors_file = _c_extract_path(base, "sponsors") / "from_teams.json"
        assert sponsors_file.exists()
        sponsors = json.loads(sponsors_file.read_text(encoding="utf-8"))
        assert "None" in sponsors
        assert elf in sponsors

        teams_file = _c_extract_path(base, "teams") / "from_teams.json"
        assert teams_file.exists()
        teams = json.loads(teams_file.read_text(encoding="utf-8"))
        assert toleman in teams

        countries_file = _c_extract_path(base, "countries") / "from_teams.json"
        assert countries_file.exists()
        countries = json.loads(countries_file.read_text(encoding="utf-8"))
        assert uk in countries
        assert france in countries

    def test_skips_null_livery_colour_and_sponsor_values(
        self,
        tmp_path: Path,
    ) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {
                "team": "AGS",
                "racing_series": {
                    "formula_one": {
                        "liveries": [
                            {
                                "season": [{"year": 1986}],
                                "main_colours": ["White"],
                                "additional_colours": None,
                                "main_sponsors": None,
                                "additional_major_sponsors": ["Jolly Club"],
                            },
                        ],
                    },
                },
            },
        ]
        _write_json(_b_merge_path(base, "teams") / "teams.json", payload)

        extract_layer_zero_phase_c(base)

        colors_file = _c_extract_path(base, "colors") / "from_teams.json"
        colors = json.loads(colors_file.read_text(encoding="utf-8"))
        assert colors == ["White"]

        sponsors_file = _c_extract_path(base, "sponsors") / "from_teams.json"
        sponsors = json.loads(sponsors_file.read_text(encoding="utf-8"))
        assert sponsors == ["Jolly Club"]

    def test_extracts_livery_sponsors_field(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [
            {
                "team": "SomeTeam",
                "racing_series": {
                    "formula_one": {
                        "liveries": [
                            {
                                "season": [{"year": 2000}],
                                "main_colours": ["Silver"],
                                "livery_sponsors": ["ATS Wheels"],
                            },
                        ],
                    },
                },
            },
        ]
        _write_json(_b_merge_path(base, "teams") / "teams.json", payload)

        extract_layer_zero_phase_c(base)

        sponsors_file = _c_extract_path(base, "sponsors") / "from_teams.json"
        assert sponsors_file.exists()
        sponsors = json.loads(sponsors_file.read_text(encoding="utf-8"))
        assert "ATS Wheels" in sponsors

    def test_skips_team_without_formula_one(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [{"team": "Privateer", "racing_series": {}}]
        _write_json(_b_merge_path(base, "teams") / "teams.json", payload)

        extract_layer_zero_phase_c(base)

        assert not (_c_extract_path(base, "colors") / "from_teams.json").exists()
        assert not (_c_extract_path(base, "sponsors") / "from_teams.json").exists()
