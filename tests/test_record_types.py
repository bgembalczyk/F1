from typing import get_type_hints

from models import records, scrape_types


def test_record_type_annotations():
    link_hints = get_type_hints(records.LinkRecord)
    season_hints = get_type_hints(records.SeasonRecord)
    driver_hints = get_type_hints(records.DriverRecord)
    circuit_hints = get_type_hints(records.CircuitRecord)

    assert link_hints == {"text": str, "url": str | None}
    assert season_hints == {"year": int, "url": str}
    assert "driver" in driver_hints
    assert "grands_prix" in circuit_hints


def test_scrape_type_annotations():
    season_hints = get_type_hints(scrape_types.SeasonRefPayload)
    driver_row_hints = get_type_hints(scrape_types.DriverRow)
    constructor_row_hints = get_type_hints(scrape_types.ConstructorRow)
    circuit_row_hints = get_type_hints(scrape_types.CircuitRow)

    assert season_hints == {"year": int, "url": str | None}
    assert "driver" in driver_row_hints
    assert "constructor" in constructor_row_hints
    assert "circuit" in circuit_row_hints
