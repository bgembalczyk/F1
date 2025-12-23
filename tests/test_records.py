from models.records import (
    CircuitCompleteRecord,
    CircuitDetailsRecord,
    CircuitRecord,
    DriverRecord,
    DriversChampionshipsRecord,
    LinkRecord,
    SeasonRecord,
)


def test_link_and_season_records_have_expected_keys() -> None:
    assert LinkRecord.__required_keys__ == {"text", "url"}
    assert SeasonRecord.__required_keys__ == {"year", "url"}


def test_driver_record_structure() -> None:
    assert DriverRecord.__required_keys__ == {
        "driver",
        "is_active",
        "is_world_champion",
        "nationality",
        "seasons_competed",
        "drivers_championships",
    }
    assert DriverRecord.__optional_keys__ == {
        "race_entries",
        "race_starts",
        "pole_positions",
        "race_wins",
        "podiums",
        "fastest_laps",
        "points",
    }
    assert DriversChampionshipsRecord.__required_keys__ == {"count", "seasons"}


def test_circuit_record_structure() -> None:
    assert CircuitRecord.__required_keys__ == {
        "circuit",
        "circuit_status",
        "type",
        "direction",
        "location",
        "country",
        "last_length_used_km",
        "last_length_used_mi",
        "turns",
        "grands_prix",
        "seasons",
        "grands_prix_held",
    }


def test_circuit_details_and_complete_records() -> None:
    assert CircuitDetailsRecord.__required_keys__ == {"url", "infobox", "tables"}
    assert CircuitCompleteRecord.__optional_keys__ >= {
        "name",
        "url",
        "circuit_status",
        "type",
        "direction",
        "grands_prix",
        "seasons",
        "grands_prix_held",
        "location",
        "fia_grade",
        "history",
        "layouts",
    }
