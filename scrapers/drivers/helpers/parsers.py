import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from bs4 import BeautifulSoup

from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.drivers.helpers.regex import ANGLE_RE
from scrapers.drivers.helpers.regex import CONFIG_TYPE_RE
from scrapers.drivers.helpers.regex import MAX_CYLINDERS_RE
from scrapers.drivers.helpers.regex import RANGE_RE
from scrapers.drivers.helpers.regex import UNIT_RE


def _extract_visible_text(ctx: ColumnContext) -> str:
    if ctx.cell is None:
        return clean_wiki_text((ctx.clean_text or ctx.raw_text or "").strip())

    soup = BeautifulSoup(str(ctx.cell), "html.parser")
    for hidden in soup.select('[style*="display:none"]'):
        hidden.decompose()
    return clean_wiki_text(soup.get_text(" ", strip=True))


def parse_entries_starts(ctx: ColumnContext) -> Tuple[Optional[int], Optional[int]]:
    text = _extract_visible_text(ctx)
    if not text:
        return None, None

    values = [int(value) for value in re.findall(r"\d+", text)]
    if not values:
        return None, None

    entries = values[0]
    starts = values[1] if len(values) > 1 else None
    return entries, starts


def parse_points_from_cell(ctx: ColumnContext) -> float | None:
    text = _extract_visible_text(ctx)
    return parse_float_from_text(text)


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_unit(unit: str) -> str:
    normalized = unit.strip().lower()
    if normalized in {"l", "litre", "litres"}:
        return "L"
    if normalized in {"cm3", "cm³", "cc"}:
        return "cc"
    return unit.strip()


def parse_unit_list(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    values: List[Dict[str, Any]] = []
    for match in UNIT_RE.finditer(text):
        values.append(
            {
                "value": parse_number(match.group("value")),
                "unit": normalize_unit(match.group("unit")),
            }
        )
    return values


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
        "value": parse_number(match.group(1)),
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
        "min": {"value": parse_number(match.group("min")), "unit": unit_label},
        "max": {"value": parse_number(match.group("max")), "unit": unit_label},
    }


def parse_numeric_range(text: str) -> dict[str, Any] | None:
    match = RANGE_RE.search(text)
    if not match:
        return None
    return {
        "min": parse_number(match.group("min")),
        "max": parse_number(match.group("max")),
    }


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


def parse_engine_rpm_limit(ctx) -> dict[str, Any]:
    text = ctx.clean_text or ""
    lower_text = text.lower()
    has_limit = not lower_text.startswith("no limit")
    if not has_limit:
        return None

    limit_range = parse_numeric_range(text)
    if limit_range is None:
        value = parse_number(text)
        limit_range = {"min": value, "max": value}
    return {"limit": limit_range}
