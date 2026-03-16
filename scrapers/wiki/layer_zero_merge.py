import json
import re
from pathlib import Path


FORMULA_ONE_SERIES = ["Formula One"]
CHASSIS_CONSTRUCTOR_DOMAINS = {"constructors", "chassis_constructors"}
FORMER_CONSTRUCTORS_SOURCE = "f1_former_constructors.json"
INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE = "f1_indianapolis_only_constructors.json"
TYRE_MANUFACTURERS_SOURCE = "f1_tyre_manufacturers_by_season.json"

CIRCUITS_FORMULA_ONE_FIELDS = {
    "circuit_status",
    "last_length_used_km",
    "last_length_used_mi",
    "turns",
    "grands_prix",
    "seasons",
    "grands_prix_held",
}
CONSTRUCTORS_FORMULA_ONE_FIELDS = {
    "engine",
    "licensed_in",
    "based_in",
    "seasons",
    "races_entered",
    "races_started",
    "drivers",
    "total_entries",
    "wins",
    "points",
    "poles",
    "fastest_laps",
    "podiums",
    "wcc_titles",
    "wdc_titles",
    "antecedent_teams",
    "status",
}
ENGINES_FORMULA_ONE_FIELDS = {
    "manufacturer_status",
    "engines_built_in",
    "seasons",
    "races_entered",
    "races_started",
    "wins",
    "points",
    "poles",
    "fastest_laps",
    "podiums",
    "wcc",
    "wdc",
}
GRANDS_PRIX_FORMULA_ONE_FIELDS = {
    "race_status",
    "country",
    "years_held",
    "circuits",
    "total",
}


def _build_racing_series(formula_one: dict[str, object]) -> list[dict[str, object]]:
    return [{"formula_one": formula_one}]


def _move_fields_to_formula_one(
    transformed: dict[str, object],
    fields: set[str],
) -> None:
    formula_one = {key: transformed.pop(key) for key in fields if key in transformed}
    if not formula_one:
        return
    transformed["racing_series"] = _build_racing_series(formula_one)


def _extract_red_flag(record: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in record.items()
        if key in {
            "lap",
            "restart_status",
            "winner",
            "incident",
            "failed_to_make_restart",
        }
    }


def _transform_record(domain: str, source_name: str, record: object) -> object:
    if not isinstance(record, dict):
        return record

    transformed = dict(record)

    if source_name == TYRE_MANUFACTURERS_SOURCE and "manufacturers" in transformed:
        transformed["tyre_manufacturers"] = transformed.pop("manufacturers")
    if (
        source_name == TYRE_MANUFACTURERS_SOURCE
        and isinstance(transformed.get("seasons"), list)
        and len(transformed["seasons"]) == 1
    ):
        transformed["season"] = transformed.pop("seasons")[0]

    if domain in CHASSIS_CONSTRUCTOR_DOMAINS:
        if source_name == INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE:
            constructor_text = transformed.get("constructor")
            constructor_url = transformed.get("constructor_url")
            transformed = {
                "constructor": {
                    "text": constructor_text,
                    "url": constructor_url,
                },
                "racing_series": [
                    {
                        "AAA_national_championship": [],
                        "formula_one": {
                            "status": "former",
                            "indianapolis_only": True,
                        },
                    },
                ],
            }
        elif source_name == FORMER_CONSTRUCTORS_SOURCE:
            constructor = transformed.get("constructor")
            formula_one = {
                key: value
                for key, value in transformed.items()
                if key != "constructor"
            }
            formula_one["status"] = "former"
            transformed = {
                "constructor": constructor,
                "racing_series": _build_racing_series(formula_one),
            }
        else:
            _move_fields_to_formula_one(transformed, CONSTRUCTORS_FORMULA_ONE_FIELDS)
            if "racing_series" not in transformed:
                transformed["status"] = "active"
                transformed["series"] = FORMULA_ONE_SERIES.copy()
            else:
                formula_one = transformed["racing_series"][0].setdefault("formula_one", {})
                formula_one.setdefault("status", "active")

    if domain == "circuits":
        _move_fields_to_formula_one(transformed, CIRCUITS_FORMULA_ONE_FIELDS)
        if "racing_series" not in transformed:
            transformed["series"] = FORMULA_ONE_SERIES.copy()

    if domain == "engines":
        if source_name == "f1_indianapolis_only_engine_manufacturers.json":
            transformed["racing_series"] = [
                {
                    "AAA_national_championship": [],
                    "formula_one": {
                        "status": "former",
                        "indianapolis_only": True,
                    },
                },
            ]
        elif source_name == "f1_engine_manufacturers.json":
            _move_fields_to_formula_one(transformed, ENGINES_FORMULA_ONE_FIELDS)

    if domain == "grands_prix":
        _move_fields_to_formula_one(transformed, GRANDS_PRIX_FORMULA_ONE_FIELDS)

    if domain == "teams":
        if re.fullmatch(r"f1_constructors_\d{4}\.json", source_name):
            transformed = {
                "team": transformed.get("constructor"),
                "racing_series": _build_racing_series({**transformed}),
            }
        if source_name == "f1_sponsorship_liveries.json" and "liveries" in transformed:
            transformed["racing_series"] = _build_racing_series(
                {"liveries": transformed.pop("liveries")},
            )
        if source_name == "f1_privateer_teams.json":
            formula_one = {
                key: transformed.pop(key)
                for key in ("seasons",)
                if key in transformed
            }
            formula_one["privateer"] = True
            transformed["racing_series"] = _build_racing_series(formula_one)

    if domain == "drivers":
        if source_name == "female_drivers.json":
            transformed["gender"] = "female"
        if source_name == "f1_driver_fatalities.json":
            death_fields = {
                key: transformed.pop(key)
                for key in ("date", "age")
                if key in transformed
            }
            crash_fields = {
                key: transformed.pop(key)
                for key in ("event", "circuit", "car", "session")
                if key in transformed
            }
            transformed["death"] = {
                **death_fields,
                "crash": crash_fields,
            }

    if domain == "races":
        if source_name == "f1_red_flagged_world_championship_races.json":
            transformed["championship"] = True
        if source_name == "f1_red_flagged_non_championship_races.json":
            transformed["championship"] = False
        transformed["red_flag"] = _extract_red_flag(transformed)
        for key in (
            "lap",
            "restart_status",
            "winner",
            "incident",
            "failed_to_make_restart",
        ):
            transformed.pop(key, None)

    return transformed


def _iter_transformed_records(domain: str, source_name: str, payload: object) -> list[object]:
    if isinstance(payload, list):
        return [_transform_record(domain, source_name, item) for item in payload]

    return [_transform_record(domain, source_name, payload)]


def _driver_record_key(record: object) -> str | None:
    if not isinstance(record, dict):
        return None

    driver_url = record.get("driver_url")
    if isinstance(driver_url, str) and driver_url:
        return driver_url

    driver = record.get("driver")
    if isinstance(driver, dict):
        url = driver.get("url")
        if isinstance(url, str) and url:
            return url

    return None


def _merge_driver_values(existing: object, incoming: object) -> object:
    if isinstance(existing, dict) and isinstance(incoming, dict):
        merged = dict(existing)
        for key, value in incoming.items():
            if key in merged:
                merged[key] = _merge_driver_values(merged[key], value)
            else:
                merged[key] = value
        return merged

    if isinstance(existing, list) and isinstance(incoming, list):
        merged = list(existing)
        seen = {json.dumps(item, sort_keys=True, ensure_ascii=False, default=str) for item in merged}
        for item in incoming:
            serialized = json.dumps(item, sort_keys=True, ensure_ascii=False, default=str)
            if serialized in seen:
                continue
            seen.add(serialized)
            merged.append(item)
        return merged

    if existing in (None, "", []):
        return incoming

    return existing


def _merge_duplicate_drivers(records: list[object]) -> list[object]:
    merged_records: list[object] = []
    key_to_index: dict[str, int] = {}

    for record in records:
        key = _driver_record_key(record)
        if key is None or not isinstance(record, dict):
            merged_records.append(record)
            continue

        index = key_to_index.get(key)
        if index is None:
            key_to_index[key] = len(merged_records)
            merged_records.append(record)
            continue

        existing = merged_records[index]
        if isinstance(existing, dict):
            merged_records[index] = _merge_driver_values(existing, record)

    return merged_records


def _season_sort_key(record: object) -> tuple[int, str]:
    if not isinstance(record, dict):
        return (1, "")

    season = record.get("season")
    if isinstance(season, int):
        return (0, str(season).zfill(10))

    return (1, "")


def _driver_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""

    driver_value = record.get("driver")
    if isinstance(driver_value, dict):
        driver_text = str(driver_value.get("text", ""))
    else:
        driver_text = str(driver_value or "")

    name_parts = driver_text.split(" ", 1)
    if len(name_parts) == 1:
        return driver_text.strip().casefold()
    return name_parts[1].strip().casefold()


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

        if domain_dir.name == "drivers":
            merged_records = _merge_duplicate_drivers(merged_records)
            merged_records = sorted(merged_records, key=_driver_sort_key)

        if domain_dir.name == "seasons":
            merged_records = sorted(merged_records, key=_season_sort_key)

        merged_path = domain_dir / f"{domain_dir.name}.json"
        merged_path.write_text(
            json.dumps(merged_records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
