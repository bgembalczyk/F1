from collections.abc import Mapping
from typing import Any

from models.records.field_normalizer import FieldNormalizer


def normalize_points(normalizer: FieldNormalizer, value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        normalized = dict(value)
        for key in ("championship_points", "total_points"):
            if key in normalized:
                normalized[key] = normalizer.normalize_float(
                    normalized.get(key),
                    f"points.{key}",
                )
        return normalized
    if isinstance(value, int | float | str):
        return normalizer.normalize_float(value, "points")
    return value


def normalize_optional_link_or_string(
    normalizer: FieldNormalizer,
    value: Any,
    field_name: str,
) -> Any:
    if isinstance(value, Mapping):
        return normalizer.normalize_link(value, field_name)
    if isinstance(value, str):
        return normalizer.normalize_string(value)
    return None


def normalize_optional_link_list_or_link_or_string(
    normalizer: FieldNormalizer,
    value: Any,
    field_name: str,
) -> Any:
    if isinstance(value, list):
        return normalizer.normalize_link_list(value, field_name)
    normalized = normalize_optional_link_or_string(normalizer, value, field_name)
    if normalized is not None:
        return normalized
    return None
