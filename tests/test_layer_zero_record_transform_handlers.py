from layers.zero.merge import _circuits_domain_handler
from layers.zero.merge import _constructor_domain_handler
from layers.zero.merge import _drivers_domain_handler
from layers.zero.merge import _engines_domain_handler
from layers.zero.merge import _grands_prix_domain_handler
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
