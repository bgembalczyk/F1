import re
from typing import Any
from typing import Callable, TypeVar, Iterable
from typing import Dict

from scrapers.base.constants import ANGLE_RE
from scrapers.base.constants import CONFIG_TYPE_RE
from scrapers.base.constants import MAX_CYLINDERS_RE
from scrapers.base.constants import RANGE_RE
from scrapers.base.table.columns.context import ColumnContext

T = TypeVar("T")


# ============================================================================
# Text Parsing
# ============================================================================


def parse_number(
    text: str | None,
    *,
    pattern: str,
    cast: Callable[[str], T],
    group: int | str = 0,
    normalizers: Iterable[Callable[[str], str]] | None = None,
) -> T | None:
    """Generic helper for extracting numbers with regex and casting."""
    if not text:
        return None

    match = re.search(pattern, text)
    if not match:
        return None

    raw = match.group(group)
    for normalize in normalizers or []:
        raw = normalize(raw)

    try:
        return cast(raw)
    except (TypeError, ValueError):
        return None


def parse_numeric_value(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_int_from_text(text: str) -> int | None:
    """Wyciąga pierwszą sensowną liczbę całkowitą z tekstu (ignoruje przecinki 1,234)."""
    return parse_number(
        text,
        pattern=r"[-+]?\d[\d,]*",
        cast=int,
        normalizers=(lambda s: s.replace(",", ""),),
    )


def parse_float_from_text(text: str) -> float | None:
    """Wyciąga pierwszą sensowną liczbę zmiennoprzecinkową z tekstu (ignoruje przecinki 1,234.5)."""
    return parse_number(
        text,
        pattern=r"[-+]?\d[\d,]*\.?\d*",
        cast=float,
        normalizers=(lambda s: s.replace(",", ""),),
    )


def parse_number_with_unit(text: str | None, *, unit: str) -> float | None:
    """Extract a float immediately followed by the given unit."""
    return parse_number(
        text,
        pattern=rf"([-+]?[0-9][0-9,]*(?:\.[0-9]+)?)\s*{re.escape(unit)}",
        cast=float,
        group=1,
        normalizers=(lambda s: s.replace(",", ""),),
    )


def parse_configuration(ctx: ColumnContext) -> Dict[str, Any] | None:
    text = ctx.clean_text or ""
    if not text:
        return None

    max_cylinders = None
    max_cylinders_match = MAX_CYLINDERS_RE.search(text)
    if max_cylinders_match:
        max_cylinders = int(max_cylinders_match.group("value"))

    parts = [part.strip() for part in re.split(r"\s*\+\s*", text) if part.strip()]
    base_text = parts[0] if parts else text
    extras = parts[1:] if len(parts) > 1 else []

    angle = None
    angle_match = ANGLE_RE.search(base_text)
    if angle_match:
        angle = {"value": parse_number(angle_match.group("value")), "unit": "deg"}
        base_text = ANGLE_RE.sub("", base_text).strip()

    type_match = CONFIG_TYPE_RE.search(base_text)
    config_type = type_match.group(1) if type_match else None
    if max_cylinders is None and config_type:
        digits_match = re.search(r"\d+", config_type)
        if digits_match:
            max_cylinders = int(digits_match.group(0))

    return {
        "text": text,
        "max_cylinders": max_cylinders,
        "angle": angle,
        "type": config_type,
        "extras": extras,
    }


def parse_numeric_range(text: str) -> dict[str, Any] | None:
    match = RANGE_RE.search(text)
    if not match:
        return None
    return {
        "min": parse_numeric_value(match.group("min")),
        "max": parse_numeric_value(match.group("max")),
    }


def parse_unit_value(
    text: str, unit: str, *, output_unit: str | None = None
) -> dict[str, Any] | None:
    match = re.search(
        rf"([-+]?\d[\d,]*(?:\.\d+)?)\s*{re.escape(unit)}\b",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    return {
        "value": parse_numeric_value(match.group(1)),
        "unit": output_unit or unit,
    }


def parse_range_with_unit(
    text: str, unit: str, *, output_unit: str | None = None
) -> dict[str, Any] | None:
    match = re.search(
        rf"(?P<min>[-+]?\d[\d,]*(?:\.\d+)?)\s*[–-]\s*(?P<max>[-+]?\d[\d,]*(?:\.\d+)?)\s*{re.escape(unit)}\b",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    unit_label = output_unit or unit
    return {
        "min": {"value": parse_numeric_value(match.group("min")), "unit": unit_label},
        "max": {"value": parse_numeric_value(match.group("max")), "unit": unit_label},
    }


def parse_engine_rpm_limit(ctx) -> dict[str, Any]:
    text = ctx.clean_text or ""
    lower_text = text.lower()
    has_limit = not lower_text.startswith("no limit")
    if not has_limit:
        return None

    limit_range = parse_numeric_range(text)
    if limit_range is None:
        value = parse_numeric_value(text)
        limit_range = {"min": value, "max": value}
    return {"limit": limit_range}


def parse_fuel_flow_rate(ctx) -> dict[str, Any]:
    text = ctx.clean_text or ""
    lower_text = text.lower()
    has_limit = not lower_text.startswith("no limit")
    if not has_limit:
        return None

    return {
        "rate": parse_unit_value(text, "kg/h", output_unit="kg/h"),
        "applies_above_rpm": parse_unit_value(text, "RPM", output_unit="RPM"),
    }


def parse_fuel_injection_pressure_limit(ctx) -> dict[str, Any]:
    text = ctx.clean_text or ""
    lower_text = text.lower()
    has_limit = not lower_text.startswith("no limit")
    if not has_limit:
        return None
    return {"limit": parse_unit_value(text, "bar", output_unit="bar")}


def parse_fuel_limit_per_race(ctx) -> dict[str, Any]:
    text = ctx.clean_text or ""
    lower_text = text.lower()
    has_limit = not lower_text.startswith("no limit")
    is_estimated = "approx" in lower_text

    range_kg = parse_range_with_unit(text, "kg", output_unit="kg")
    range_l = parse_range_with_unit(text, "l", output_unit="L")

    return {
        "has_limit": has_limit,
        "is_estimated": is_estimated,
        "range_kg": range_kg,
        "range_l": range_l,
    }
