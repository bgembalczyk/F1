import logging

from models.contracts.circuit import CircuitContract
from models.contracts.driver import DriverContract
from models.contracts.helpers import map_record_to_contract
from models.contracts.helpers import resolve_record_contract
from models.contracts.points import PointsContract
from models.serializers import to_dict_any


def test_contract_can_handle_rules_are_explicit():
    driver_record = {"driver": {"text": "A", "url": None}, "is_active": True}
    circuit_record = {
        "circuit": {"text": "Monza", "url": None},
        "circuit_status": "current",
    }
    points_record = {"seasons": [{"year": 2024}], "1st": 25}

    assert DriverContract.can_handle(driver_record)
    assert CircuitContract.can_handle(circuit_record)
    assert PointsContract.can_handle(points_record)


def test_resolver_uses_deterministic_registry_order_for_ambiguous_record(caplog):
    ambiguous_record = {
        "driver": {"text": "A", "url": None},
        "is_active": True,
        "circuit": {"text": "Monza", "url": None},
        "circuit_status": "current",
    }

    with caplog.at_level(logging.WARNING):
        resolved = resolve_record_contract(ambiguous_record)

    assert resolved is DriverContract
    assert "Niejednoznaczne dopasowanie kontraktu" in caplog.text


def test_map_record_to_contract_falls_back_to_raw_record_when_no_match(caplog):
    unknown_record = {"foo": "bar"}

    with caplog.at_level(logging.DEBUG):
        mapped = map_record_to_contract(unknown_record)

    assert mapped == unknown_record
    assert "Brak dopasowania kontraktu" in caplog.text


def test_to_dict_any_uses_contract_resolver_for_mappings():
    record = {
        "driver": {"text": "A", "url": None},
        "is_active": True,
        "unknown": "x",
    }

    serialized = to_dict_any(record)

    assert serialized["driver"] == {"text": "A", "url": None}
    assert serialized["is_active"] is True
    assert serialized["unknown"] == "x"
