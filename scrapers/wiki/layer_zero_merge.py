import json
from pathlib import Path


FORMULA_ONE_SERIES = ["Formula One"]


def _extract_red_flag(record: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in record.items()
        if key not in {"season", "grand_prix", "event"}
    }


def _transform_record(domain: str, source_name: str, record: object) -> object:
    if not isinstance(record, dict):
        return record

    transformed = dict(record)

    if domain == "circuits":
        transformed["series"] = FORMULA_ONE_SERIES.copy()

    if domain == "constructors":
        transformed["status"] = "active"
        transformed["series"] = FORMULA_ONE_SERIES.copy()

    if domain == "drivers":
        if source_name == "female_drivers.json":
            transformed["gender"] = "female"
        if source_name == "f1_driver_fatalities.json":
            transformed["fatality"] = {
                key: value for key, value in transformed.items() if key != "driver"
            }

    if domain == "races":
        if source_name == "f1_red_flagged_world_championship_races.json":
            transformed["non_championship"] = "true"
        transformed["red_flag"] = _extract_red_flag(transformed)

    return transformed


def _iter_transformed_records(domain: str, source_name: str, payload: object) -> list[object]:
    if isinstance(payload, list):
        return [_transform_record(domain, source_name, item) for item in payload]

    return [_transform_record(domain, source_name, payload)]


def merge_layer_zero_raw_outputs(base_wiki_dir: Path) -> None:
    layer_zero_dir = base_wiki_dir / "layers" / "0_layer"
    if not layer_zero_dir.exists():
        return

    for domain_dir in sorted(p for p in layer_zero_dir.iterdir() if p.is_dir()):
        raw_dir = domain_dir / "raw"
        if not raw_dir.exists() or not raw_dir.is_dir():
            continue

        if domain_dir.name in {"points", "rules"}:
            continue

        merged_records: list[object] = []
        for json_path in sorted(raw_dir.rglob("*.json")):
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            merged_records.extend(
                _iter_transformed_records(domain_dir.name, json_path.name, payload),
            )

        if not merged_records:
            continue

        merged_path = domain_dir / f"{domain_dir.name}.json"
        merged_path.write_text(
            json.dumps(merged_records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
