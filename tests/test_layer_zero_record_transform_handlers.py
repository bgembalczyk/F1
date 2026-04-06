from layers.zero.merge import _circuits_domain_handler
from layers.zero.merge import _constructor_domain_handler
from layers.zero.merge import _drivers_domain_handler
from layers.zero.merge import _engines_domain_handler
from layers.zero.merge import _expand_season_records
from layers.zero.merge import _grands_prix_domain_handler
from layers.zero.merge import _post_process_domain_records
from layers.zero.merge import _races_domain_handler
from layers.zero.merge import _resolve_record_transform_handlers
from layers.zero.merge import _teams_domain_handler
from layers.zero.merge import _tyre_manufacturers_handler

SEASON_YEAR = 2025
CONSTRUCTOR_WINS = 198
CIRCUIT_GRANDS_PRIX_HELD = 74
ENGINE_WINS = 89
DRIVER_RACE_ENTRIES = 350
DRIVER_RACE_STARTS = 348


def test_tyre_manufacturers_transform_handler() -> None:
    transformed = _tyre_manufacturers_handler(
        domain="seasons",
        source_name="f1_tyre_manufacturers_by_season.json",
        record={"manufacturers": ["A"], "seasons": [SEASON_YEAR], "x": 1},
    )

    assert transformed["tyre_manufacturers"] == ["A"]
    assert transformed["season"] == SEASON_YEAR
    assert transformed["x"] == 1


def test_constructor_domain_transform_handler() -> None:
    transformed = _constructor_domain_handler(
        domain="constructors",
        source_name="f1_constructors_2026.json",
        record={
            "constructor": "McLaren",
            "engine": "Mercedes",
            "wins": CONSTRUCTOR_WINS,
        },
    )

    assert transformed["constructor"] == "McLaren"
    assert transformed["racing_series"]["formula_one"]["wins"] == CONSTRUCTOR_WINS
    assert transformed["racing_series"]["formula_one"]["status"] == "active"
    assert "engine" in transformed


def test_constructor_domain_handler_chassis_current_list() -> None:
    transformed = _constructor_domain_handler(
        domain="chassis_constructors",
        source_name="f1_constructors_2026.json",
        record={
            "constructor": {
                "chassis_constructor": {"text": "Alpine", "url": "https://example.com"},
                "engine_constructor": {"text": "Mercedes", "url": "https://engine"},
            },
            "antecedent_teams": [{"text": "Toleman"}],
        },
    )

    assert transformed["chassis_constructor"] == {
        "text": "Alpine",
        "url": "https://example.com",
    }
    assert transformed["engine_constructors"] == [
        {"text": "Mercedes", "url": "https://engine"},
    ]
    assert transformed["antecedent_teams"] == [{"text": "Toleman"}]
    assert "constructor" not in transformed
    assert next(iter(transformed)) == "chassis_constructor"


def test_constructor_domain_handler_constructor_alias_current_list() -> None:
    transformed = _constructor_domain_handler(
        domain="constructor",
        source_name="f1_constructors_2026.json",
        record={
            "constructor": {
                "chassis_constructor": {"text": "Alpine", "url": "https://example.com"},
                "engine_constructor": {"text": "Mercedes", "url": "https://engine"},
            },
            "antecedent_teams": [{"text": "Toleman"}],
        },
    )

    assert transformed["chassis_constructor"] == {
        "text": "Alpine",
        "url": "https://example.com",
    }
    assert transformed["engine_constructors"] == [
        {"text": "Mercedes", "url": "https://engine"},
    ]
    assert transformed["antecedent_teams"] == [{"text": "Toleman"}]
    assert "constructor" not in transformed


def test_constructor_domain_transform_handler_for_chassis_alias_current_list() -> None:
    transformed = _constructor_domain_handler(
        domain="chassis",
        source_name="f1_constructors_2026.json",
        record={
            "constructor": {
                "chassis_constructor": {"text": "Alpine", "url": "https://example.com"},
                "engine_constructor": {"text": "Mercedes", "url": "https://engine"},
            },
            "antecedent_teams": [{"text": "Toleman"}],
        },
    )

    assert transformed["chassis_constructor"] == {
        "text": "Alpine",
        "url": "https://example.com",
    }
    assert transformed["engine_constructors"] == [
        {"text": "Mercedes", "url": "https://engine"},
    ]
    assert transformed["antecedent_teams"] == [{"text": "Toleman"}]
    assert "constructor" not in transformed




def test_constructor_domain_handler_indianapolis_only_chassis() -> None:
    transformed = _constructor_domain_handler(
        domain="chassis_constructors",
        source_name="f1_indianapolis_only_constructors.json",
        record={
            "chassis_constructor": {
                "text": "Adams",
                "url": "https://en.wikipedia.org/wiki/Adams_(constructor)",
            },
        },
    )

    assert transformed["chassis_constructor"] == {
        "text": "Adams",
        "url": "https://en.wikipedia.org/wiki/Adams_(constructor)",
    }
    assert transformed["racing_series"] == {
        "AAA_national_championship": [],
        "formula_one": {
            "status": "former",
            "indianapolis_only": True,
        },
    }
    assert "constructor" not in transformed


def test_constructor_domain_handler_indianapolis_only() -> None:
    transformed = _constructor_domain_handler(
        domain="constructors",
        source_name="f1_indianapolis_only_constructors.json",
        record={
            "constructor": "Adams",
            "constructor_url": "https://en.wikipedia.org/wiki/Adams_(constructor)",
        },
    )

    assert transformed["constructor"] == {
        "text": "Adams",
        "url": "https://en.wikipedia.org/wiki/Adams_(constructor)",
    }
    assert transformed["racing_series"] == {
        "AAA_national_championship": [],
        "formula_one": {
            "status": "former",
            "indianapolis_only": True,
        },
    }

def test_constructor_domain_handler_chassis_former_list() -> None:
    transformed = _constructor_domain_handler(
        domain="chassis_constructors",
        source_name="f1_former_constructors.json",
        record={
            "constructor": None,
            "chassis_constructor": {"text": "AGS", "url": "https://example.com/ags"},
            "drivers": 10,
            "points": 2,
        },
    )

    assert transformed == {
        "chassis_constructor": {"text": "AGS", "url": "https://example.com/ags"},
        "drivers": 10,
        "points": 2,
        "status": "former",
    }


def test_circuits_domain_transform_handler() -> None:
    transformed = _circuits_domain_handler(
        domain="circuits",
        source_name="ignored.json",
        record={"circuit": "Monza", "grands_prix_held": CIRCUIT_GRANDS_PRIX_HELD},
    )

    assert (
        transformed["racing_series"]["formula_one"]["grands_prix_held"]
        == CIRCUIT_GRANDS_PRIX_HELD
    )


def test_circuits_domain_transform_handler_sorts_formula_one_keys() -> None:
    transformed = _circuits_domain_handler(
        domain="circuits",
        source_name="ignored.json",
        record={
            "circuit": "Monza",
            "turns": 11,
            "circuit_status": "active",
            "grands_prix_held": CIRCUIT_GRANDS_PRIX_HELD,
        },
    )

    formula_one = transformed["racing_series"]["formula_one"]
    assert list(formula_one) == sorted(formula_one)


def test_engines_domain_transform_handler() -> None:
    transformed = _engines_domain_handler(
        domain="engines",
        source_name="f1_engine_manufacturers.json",
        record={"engine_manufacturer": "Honda", "wins": ENGINE_WINS},
    )

    assert transformed["engine_constructor"] == "Honda"
    assert transformed["racing_series"]["formula_one"]["wins"] == ENGINE_WINS


def test_grands_prix_domain_transform_handler() -> None:
    transformed = _grands_prix_domain_handler(
        domain="grands_prix",
        source_name="ignored.json",
        record={"grand_prix": "Italian Grand Prix", "years_held": [1921, 2025]},
    )

    assert transformed["racing_series"]["formula_one"]["years_held"] == [1921, 2025]


def test_teams_domain_transform_handler() -> None:
    transformed = _teams_domain_handler(
        domain="teams",
        source_name="f1_privateer_teams.json",
        record={"team": "Scuderia Centro Sud", "seasons": [1956, 1965]},
    )

    assert transformed["racing_series"]["formula_one"]["privateer"] is True
    assert transformed["racing_series"]["formula_one"]["seasons"] == [1956, 1965]


def test_teams_domain_transform_handler_for_current_constructors_list() -> None:
    transformed = _teams_domain_handler(
        domain="teams",
        source_name="f1_constructors_2026.json",
        record={
            "constructor": {
                "chassis_constructor": {"text": "Alpine", "url": "https://example.com"},
                "engine_constructor": {"text": "Mercedes", "url": "https://engine"},
            },
            "antecedent_teams": [{"text": "Toleman"}],
        },
    )

    assert transformed["team"] == {"text": "Alpine", "url": "https://example.com"}
    assert transformed["racing_series"]["formula_one"]["constructors"] == [
        {
            "chassis_constructor": {"text": "Alpine", "url": "https://example.com"},
            "engine_constructor": {"text": "Mercedes", "url": "https://engine"},
        },
    ]
    assert transformed["racing_series"]["formula_one"]["antecedent_teams"] == [
        {"text": "Toleman"},
    ]


def test_drivers_domain_transform_handler() -> None:
    transformed = _drivers_domain_handler(
        domain="drivers",
        source_name="f1_drivers.json",
        record={
            "driver": "Lewis Hamilton",
            "entries": DRIVER_RACE_ENTRIES,
            "starts": DRIVER_RACE_STARTS,
        },
    )

    assert transformed["driver"] == "Lewis Hamilton"
    assert (
        transformed["racing_series"]["formula_one"]["race_entries"]
        == DRIVER_RACE_ENTRIES
    )
    assert (
        transformed["racing_series"]["formula_one"]["race_starts"] == DRIVER_RACE_STARTS
    )


def test_races_domain_transform_handler() -> None:
    transformed = _races_domain_handler(
        domain="races",
        source_name="f1_red_flagged_world_championship_races.json",
        record={"race": "A", "lap": "54/72", "incident": "rain"},
    )

    assert transformed["championship"] is True
    assert transformed["red_flag"] == {"lap": "54/72", "incident": "rain"}
    assert "lap" not in transformed


def test_resolve_record_transform_handlers_domain_fallback() -> None:
    handlers = _resolve_record_transform_handlers(
        domain="teams",
        source_name="unknown.json",
    )

    assert handlers == (_teams_domain_handler,)


def test_resolve_record_transform_handlers_for_chassis_constructors_domain() -> None:
    handlers = _resolve_record_transform_handlers(
        domain="chassis_constructors",
        source_name="f1_constructors_2026.json",
    )

    assert handlers == (_constructor_domain_handler,)


def test_resolve_record_transform_handlers_includes_global_source_pipeline() -> None:
    handlers = _resolve_record_transform_handlers(
        domain="seasons",
        source_name="f1_tyre_manufacturers_by_season.json",
    )

    assert handlers == (_tyre_manufacturers_handler,)


def test_engines_domain_postprocess_sorts_by_manufacturer() -> None:
    processed = _post_process_domain_records(
        "engines",
        [
            {"engine_constructor": "Renault"},
            {"engine_constructor": "Alfa Romeo"},
            {"engine_constructor": {"text": "BMW", "url": "https://example.com/bmw"}},
        ],
    )

    assert [
        record["engine_constructor"]["text"]
        if isinstance(record["engine_constructor"], dict)
        else record["engine_constructor"]
        for record in processed
    ] == ["Alfa Romeo", "BMW", "Renault"]


def test_chassis_constructors_domain_postprocess_sorts_by_chassis_constructor() -> None:
    processed = _post_process_domain_records(
        "chassis_constructors",
        [
            {"chassis_constructor": {"text": "Williams"}},
            {"chassis_constructor": {"text": "Alpine"}},
            {"chassis_constructor": {"text": "Ferrari"}},
        ],
    )

    assert [record["chassis_constructor"]["text"] for record in processed] == [
        "Alpine",
        "Ferrari",
        "Williams",
    ]


def test_circuits_domain_postprocess_sorts_by_circuit_text() -> None:
    processed = _post_process_domain_records(
        "circuits",
        [
            {"circuit": {"text": "Monza"}},
            {"circuit": {"text": "Bahrain International Circuit"}},
            {"circuit": {"text": "Spa-Francorchamps"}},
        ],
    )

    assert [record["circuit"]["text"] for record in processed] == [
        "Bahrain International Circuit",
        "Monza",
        "Spa-Francorchamps",
    ]


def test_constructors_domain_postprocess_sorts_by_chassis_then_engine() -> None:
    processed = _post_process_domain_records(
        "constructors",
        [
            {
                "constructor": {
                    "chassis_constructor": {"text": "Williams"},
                    "engine_constructor": {"text": "Mercedes"},
                },
            },
            {
                "constructor": {
                    "chassis_constructor": {"text": "Ferrari"},
                    "engine_constructor": {"text": "Ferrari"},
                },
            },
            {
                "constructor": {
                    "chassis_constructor": {"text": "Williams"},
                    "engine_constructor": {"text": "Honda"},
                },
            },
        ],
    )

    assert [
        (
            item["constructor"]["chassis_constructor"]["text"],
            item["constructor"]["engine_constructor"]["text"],
        )
        for item in processed
    ] == [("Ferrari", "Ferrari"), ("Williams", "Honda"), ("Williams", "Mercedes")]


def test_countries_domain_postprocess_sorts_dicts_and_strings_together() -> None:
    processed = _post_process_domain_records(
        "countries",
        [
            {"text": "Poland"},
            "Belgium",
            {"text": "Argentina"},
            "Brazil",
        ],
    )

    assert processed == [{"text": "Argentina"}, "Belgium", "Brazil", {"text": "Poland"}]


def test_grands_prix_domain_postprocess_sorts_by_race_title() -> None:
    processed = _post_process_domain_records(
        "grands_prix",
        [
            {"race_title": {"text": "Monaco Grand Prix"}},
            {"race_title": {"text": "Australian Grand Prix"}},
            {"race_title": {"text": "Belgian Grand Prix"}},
        ],
    )

    assert [record["race_title"]["text"] for record in processed] == [
        "Australian Grand Prix",
        "Belgian Grand Prix",
        "Monaco Grand Prix",
    ]


def test_races_domain_postprocess_sorts_by_season_and_grand_prix_or_event() -> None:
    processed = _post_process_domain_records(
        "races",
        [
            {"season": 2020, "grand_prix": {"text": "Monaco"}},
            {"season": 2019, "event": {"text": "Goodwood Festival"}},
            {"season": 2019, "grand_prix": {"text": "Australian"}},
        ],
    )

    assert [
        (item["season"], item.get("grand_prix") or item.get("event"))
        for item in processed
    ] == [
        (2019, {"text": "Australian"}),
        (2019, {"text": "Goodwood Festival"}),
        (2020, {"text": "Monaco"}),
    ]


def test_sponsors_domain_postprocess_sorts_dicts_and_strings_together() -> None:
    processed = _post_process_domain_records(
        "sponsors",
        [
            {"text": "Shell"},
            "Agip",
            {"text": "Mobil"},
            "BP",
        ],
    )

    assert processed == ["Agip", "BP", {"text": "Mobil"}, {"text": "Shell"}]


def test_teams_domain_postprocess_sorts_by_team_or_text_equally() -> None:
    processed = _post_process_domain_records(
        "teams",
        [
            {"team": {"text": "Williams"}},
            {"text": "Alpine"},
            {"team": {"text": "Ferrari"}},
        ],
    )

    assert [
        (item.get("team") or item.get("text"))["text"]
        if isinstance(item.get("team") or item.get("text"), dict)
        else item.get("team") or item.get("text")
        for item in processed
    ] == ["Alpine", "Ferrari", "Williams"]


def test_expand_season_records_for_engine_regulations() -> None:
    expanded = _expand_season_records(
        domain="seasons",
        source_name="f1_engine_regulations.json",
        record={
            "seasons": [{"year": 1950}, {"year": 1951}],
            "configuration": "V12",
            "fuel": "petrol",
        },
    )

    assert expanded == [
        {
            "season": {"year": 1950},
            "engine_regulations": {"configuration": "V12", "fuel": "petrol"},
        },
        {
            "season": {"year": 1951},
            "engine_regulations": {"configuration": "V12", "fuel": "petrol"},
        },
    ]


def test_expand_season_records_for_engine_restrictions_uses_year_ranges() -> None:
    expanded = _expand_season_records(
        domain="seasons",
        source_name="f1_engine_restrictions.json",
        record={
            "year": [{"year": 2000}, {"year": 2001}],
            "type_of_engine": [{"text": "V10"}],
        },
    )

    assert expanded == [
        {
            "season": {"year": 2000},
            "engine_restrictions": {"type_of_engine": [{"text": "V10"}]},
        },
        {
            "season": {"year": 2001},
            "engine_restrictions": {"type_of_engine": [{"text": "V10"}]},
        },
    ]


def test_expand_season_records_for_points_sources() -> None:
    history = _expand_season_records(
        domain="seasons",
        source_name="points_scoring_systems_history.json",
        record={
            "seasons": [{"year": 1960}],
            "drivers_championship": {"1st": 8},
        },
    )
    shortened = _expand_season_records(
        domain="seasons",
        source_name="points_scoring_systems_shortened.json",
        record={"seasons": [{"year": 2022}], "race_length_points": [{"first": 25}]},
    )
    sprint = _expand_season_records(
        domain="seasons",
        source_name="points_scoring_systems_sprint.json",
        record={"seasons": [{"year": 2021}], "first": 3},
    )

    assert history == [
        {
            "season": {"year": 1960},
            "points_scoring_system": {"drivers_championship": {"1st": 8}},
        },
    ]
    assert shortened == [
        {
            "season": {"year": 2022},
            "points_scoring_system_shortened": {
                "race_length_points": [{"first": 25}],
            },
        },
    ]
    assert sprint == [
        {
            "season": {"year": 2021},
            "points_scoring_system_sprint": {"first": 3},
        },
    ]


def test_seasons_domain_postprocess_sorts_by_nested_season_year() -> None:
    processed = _post_process_domain_records(
        "seasons",
        [
            {"season": {"year": 2021}},
            {"season": {"year": 1950}},
            {"season": {"year": 2000}},
        ],
    )

    assert [item["season"]["year"] for item in processed] == [1950, 2000, 2021]


def test_seasons_domain_postprocess_merges_duplicate_year_representations() -> None:
    processed = _post_process_domain_records(
        "seasons",
        [
            {"season": {"text": "1950", "url": "https://example.com/1950"}},
            {
                "season": {"year": 1950},
                "engine_regulations": {"configuration": "V12"},
            },
            {"season": {"text": "2000", "url": "https://example.com/2000"}},
            {"season": {"year": 2000}, "points_scoring_system": {"first": 10}},
        ],
    )

    assert processed == [
        {
            "season": {"text": "1950", "url": "https://example.com/1950", "year": 1950},
            "engine_regulations": {"configuration": "V12"},
        },
        {
            "season": {"text": "2000", "url": "https://example.com/2000", "year": 2000},
            "points_scoring_system": {"first": 10},
        },
    ]


def test_seasons_domain_postprocess_keeps_engine_regs_and_restrictions_separate() -> (
    None
):
    processed = _post_process_domain_records(
        "seasons",
        [
            {"season": {"year": 2000}, "engine_regulations": {"configuration": "V10"}},
            {
                "season": {"year": 2000},
                "engine_restrictions": {"type_of_engine": "V10"},
            },
        ],
    )

    assert processed == [
        {
            "season": {"year": 2000},
            "engine_regulations": {"configuration": "V10"},
            "engine_restrictions": {"type_of_engine": "V10"},
        },
    ]
