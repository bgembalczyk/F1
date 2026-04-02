from layers.zero.merge import _circuits_domain_handler
from layers.zero.merge import _constructor_domain_handler
from layers.zero.merge import _drivers_domain_handler
from layers.zero.merge import _engines_domain_handler
from layers.zero.merge import _grands_prix_domain_handler
from layers.zero.merge import _races_domain_handler
from layers.zero.merge import _resolve_record_meta
from layers.zero.merge import _resolve_record_transform_handlers
from layers.zero.merge import _teams_domain_handler
from layers.zero.merge import _tyre_manufacturers_handler


def test_tyre_manufacturers_transform_handler() -> None:
    transformed = _tyre_manufacturers_handler(
        meta=_resolve_record_meta("seasons", "f1_tyre_manufacturers_by_season.json"),
        record={"manufacturers": ["A"], "seasons": [2025], "x": 1},
    )

    assert transformed["tyre_manufacturers"] == ["A"]
    assert transformed["season"] == 2025
    assert transformed["x"] == 1


def test_constructor_domain_transform_handler() -> None:
    transformed = _constructor_domain_handler(
        meta=_resolve_record_meta("constructors", "f1_constructors_2026.json"),
        record={
            "constructor": "McLaren",
            "engine": "Mercedes",
            "wins": 198,
        },
    )

    assert transformed["constructor"] == "McLaren"
    assert transformed["racing_series"]["formula_one"]["wins"] == 198
    assert transformed["racing_series"]["formula_one"]["status"] == "active"
    assert "engine" in transformed


def test_circuits_domain_transform_handler() -> None:
    transformed = _circuits_domain_handler(
        meta=_resolve_record_meta("circuits", "ignored.json"),
        record={"circuit": "Monza", "grands_prix_held": 74},
    )

    assert transformed["racing_series"]["formula_one"]["grands_prix_held"] == 74


def test_engines_domain_transform_handler() -> None:
    transformed = _engines_domain_handler(
        meta=_resolve_record_meta("engines", "f1_engine_manufacturers.json"),
        record={"engine_manufacturer": "Honda", "wins": 89},
    )

    assert transformed["racing_series"]["formula_one"]["wins"] == 89


def test_grands_prix_domain_transform_handler() -> None:
    transformed = _grands_prix_domain_handler(
        meta=_resolve_record_meta("grands_prix", "ignored.json"),
        record={"grand_prix": "Italian Grand Prix", "years_held": [1921, 2025]},
    )

    assert transformed["racing_series"]["formula_one"]["years_held"] == [1921, 2025]


def test_teams_domain_transform_handler() -> None:
    transformed = _teams_domain_handler(
        meta=_resolve_record_meta("teams", "f1_privateer_teams.json"),
        record={"team": "Scuderia Centro Sud", "seasons": [1956, 1965]},
    )

    assert transformed["racing_series"]["formula_one"]["privateer"] is True
    assert transformed["racing_series"]["formula_one"]["seasons"] == [1956, 1965]


def test_drivers_domain_transform_handler() -> None:
    transformed = _drivers_domain_handler(
        meta=_resolve_record_meta("drivers", "f1_drivers.json"),
        record={"driver": "Lewis Hamilton", "entries": 350, "starts": 348},
    )

    assert transformed["driver"] == "Lewis Hamilton"
    assert transformed["racing_series"]["formula_one"]["race_entries"] == 350
    assert transformed["racing_series"]["formula_one"]["race_starts"] == 348


def test_races_domain_transform_handler() -> None:
    transformed = _races_domain_handler(
        meta=_resolve_record_meta("races", "f1_red_flagged_world_championship_races.json"),
        record={"race": "A", "lap": "54/72", "incident": "rain"},
    )

    assert transformed["championship"] is True
    assert transformed["red_flag"] == {"lap": "54/72", "incident": "rain"}
    assert "lap" not in transformed


def test_resolve_record_transform_handlers_uses_domain_fallback_when_no_source_override() -> None:
    handlers = _resolve_record_transform_handlers(
        _resolve_record_meta("teams", "unknown.json"),
    )

    assert handlers == (_teams_domain_handler,)


def test_resolve_record_transform_handlers_includes_global_source_pipeline() -> None:
    handlers = _resolve_record_transform_handlers(
        _resolve_record_meta("seasons", "f1_tyre_manufacturers_by_season.json"),
    )

    assert handlers == (_tyre_manufacturers_handler,)
