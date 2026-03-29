import json
from pathlib import Path

from scrapers.base.orchestration.components.record_loader import RecordLoader


def test_record_loader_reads_records_from_list_payload(tmp_path: Path) -> None:
    path = tmp_path / "records.json"
    path.write_text(json.dumps([{"id": 1}, "skip", {"id": 2}]), encoding="utf-8")

    loaded = RecordLoader().load(path)

    assert loaded == [{"id": 1}, {"id": 2}]


def test_record_loader_reads_records_from_dict_payload(tmp_path: Path) -> None:
    path = tmp_path / "records.json"
    path.write_text(
        json.dumps({"records": [{"id": 1}, None, {"id": 2}], "meta": {"ok": True}}),
        encoding="utf-8",
    )

    loaded = RecordLoader().load(path)

    assert loaded == [{"id": 1}, {"id": 2}]


def test_record_loader_returns_empty_list_for_unsupported_payload_shape(
    tmp_path: Path,
) -> None:
    path = tmp_path / "records.json"
    path.write_text(json.dumps({"unexpected": "shape"}), encoding="utf-8")

    loaded = RecordLoader().load(path)

    assert loaded == []
