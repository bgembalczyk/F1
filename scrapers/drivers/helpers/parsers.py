import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from bs4 import BeautifulSoup

from scrapers.base.constants import RANGE_RE
from scrapers.base.constants import UNIT_RE
from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext


def extract_visible_text(ctx: ColumnContext) -> str:
    if ctx.cell is None:
        return clean_wiki_text((ctx.clean_text or ctx.raw_text or "").strip())

    soup = BeautifulSoup(str(ctx.cell), "html.parser")
    for hidden in soup.select('[style*="display:none"]'):
        hidden.decompose()
    return clean_wiki_text(soup.get_text(" ", strip=True))


def parse_entries_starts(ctx: ColumnContext) -> Tuple[Optional[int], Optional[int]]:
    text = extract_visible_text(ctx)
    if not text:
        return None, None

    values = [int(value) for value in re.findall(r"\d+", text)]
    if not values:
        return None, None

    entries = values[0]
    starts = values[1] if len(values) > 1 else None
    return entries, starts


def parse_points_from_cell(ctx: ColumnContext) -> float | None:
    text = extract_visible_text(ctx)
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


def extract_driver_text(record: Dict[str, Any]) -> Optional[str]:
    driver = record.get("driver")
    if isinstance(driver, dict):
        text = driver.get("text")
        if isinstance(text, str):
            return text.strip()
    return None
