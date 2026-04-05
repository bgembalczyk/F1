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
            {"manufacturer": "Renault"},
            {"manufacturer": "Alfa Romeo"},
            {"manufacturer": {"text": "BMW", "url": "https://example.com/bmw"}},
        ],
    )

    assert [
        record["manufacturer"]["text"]
        if isinstance(record["manufacturer"], dict)
        else record["manufacturer"]
        for record in processed
    ] == ["Alfa Romeo", "BMW", "Renault"]


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


def test_seasons_domain_postprocess_keeps_engine_regulations_and_restrictions_separate() -> (
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
