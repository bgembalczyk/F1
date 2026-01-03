from typing import get_type_hints

from models import records


def test_record_type_annotations():
    link_hints = get_type_hints(records.LinkRecord)
    season_hints = get_type_hints(records.SeasonRecord)
    driver_hints = get_type_hints(records.DriverRecord)
    circuit_hints = get_type_hints(records.CircuitRecord)

    assert link_hints == {"text": str, "url": str | None}
    assert season_hints == {"year": int, "url": str}
    assert "driver" in driver_hints
    assert "grands_prix" in circuit_hints
