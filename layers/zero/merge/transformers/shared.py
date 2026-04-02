from __future__ import annotations

from scrapers.wiki.constants import FORMULA_ONE_SERIES
from scrapers.wiki.constants import RED_FLAG_FIELDS


def build_racing_series(formula_one: dict[str, object]) -> dict[str, object]:
    return {"formula_one": formula_one}


def move_fields_to_formula_one(transformed: dict[str, object], fields: set[str]) -> None:
    formula_one = {key: transformed.pop(key) for key in fields if key in transformed}
    if not formula_one:
        return
    transformed["racing_series"] = build_racing_series(formula_one)


def ensure_constructor_status(transformed: dict[str, object]) -> None:
    if "racing_series" not in transformed:
        transformed["status"] = "active"
        transformed["series"] = FORMULA_ONE_SERIES.copy()
        return

    racing_series = transformed.get("racing_series")
    if not isinstance(racing_series, dict):
        racing_series = {}
        transformed["racing_series"] = racing_series
    formula_one = racing_series.setdefault("formula_one", {})
    formula_one.setdefault("status", "active")


def normalize_driver_series_stats(formula_one: dict[str, object]) -> dict[str, object]:
    normalized = dict(formula_one)
    if "race_entries" not in normalized and "entries" in normalized:
        normalized["race_entries"] = normalized.pop("entries")
    else:
        normalized.pop("entries", None)

    if "race_starts" not in normalized and "starts" in normalized:
        normalized["race_starts"] = normalized.pop("starts")
    else:
        normalized.pop("starts", None)

    return normalized


def extract_red_flag(record: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in record.items() if key in RED_FLAG_FIELDS}


def pop_red_flag_fields(record: dict[str, object]) -> None:
    for key in RED_FLAG_FIELDS:
        record.pop(key, None)
