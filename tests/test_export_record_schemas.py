import logging

from models.records.schemas import DriverExportRecord
from models.records.schemas import serialize_for_json
from models.records.schemas import validate_model_contract


def test_driver_export_record_serializer_maps_to_json_dict() -> None:
    model = DriverExportRecord(
        url="https://example.com/wiki/Ayrton_Senna",
        infobox={"name": "Ayrton Senna"},
        career_results=[{"season": 1988, "wins": 8}],
    )

    payload = serialize_for_json(model)

    assert payload == {
        "url": "https://example.com/wiki/Ayrton_Senna",
        "infobox": {"name": "Ayrton Senna"},
        "career_results": [{"season": 1988, "wins": 8}],
    }


def test_model_validation_reports_missing_contract_fields(caplog) -> None:
    model = DriverExportRecord(
        url="",
        infobox={},
        career_results=[],
    )

    with caplog.at_level(logging.WARNING):
        validate_model_contract(model, logger=logging.getLogger("test.schemas"))

    assert "Brakujące pola kontraktowe" in caplog.text
    assert "career_results" in caplog.text
    assert "infobox" in caplog.text
    assert "url" in caplog.text
