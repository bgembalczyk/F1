from __future__ import annotations

import pytest

from infrastructure.export.default_export_service import build_default_export_service
from scrapers.base.export.service import ExportService


@pytest.mark.parametrize(
    "attribute_name,expected_type_name",
    [
        ("_exporter", "DataExporter"),
        ("_fieldnames_strategy", "FieldnamesStrategySelector"),
        ("_dataframe_formatter", "PandasDataFrameFormatter"),
    ],
)
def test_build_default_export_service_initializes_expected_dependencies(
    attribute_name: str,
    expected_type_name: str,
) -> None:
    service = build_default_export_service()

    assert isinstance(service, ExportService)
    assert type(getattr(service, attribute_name)).__name__ == expected_type_name


def test_default_export_service_to_csv_exports_valid_data(tmp_path) -> None:
    service = build_default_export_service()
    output = tmp_path / "drivers.csv"

    service.to_csv(
        [
            {"driver": "Lewis Hamilton", "wins": 105},
            {"driver": "Max Verstappen", "wins": 63},
        ],
        output,
    )

    content = output.read_text(encoding="utf-8")
    assert "driver,wins" in content
    assert "Lewis Hamilton,105" in content
    assert "Max Verstappen,63" in content


def test_default_export_service_to_csv_handles_empty_input(tmp_path) -> None:
    service = build_default_export_service()
    output = tmp_path / "empty.csv"

    service.to_csv([], output)

    assert output.read_text(encoding="utf-8") == ""


def test_default_export_service_to_csv_propagates_dependency_exception(
    monkeypatch,
    tmp_path,
) -> None:
    service = build_default_export_service()
    output = tmp_path / "broken.csv"

    def _raise_for_malformed_payload(*_args, **_kwargs):
        raise ValueError("malformed export payload")

    monkeypatch.setattr(service._fieldnames_strategy, "resolve", _raise_for_malformed_payload)

    with pytest.raises(ValueError, match="malformed export payload"):
        service.to_csv([{"driver": "Ayrton Senna"}], output)
