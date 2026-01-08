"""Table column parsing helpers.

This module provides backward-compatible access to column parsing helper functions.

REFACTORED (following SRP): The implementation has been reorganized into focused modules:
- driver_parsing.py: Driver-specific parsing (DriverParsingHelpers class)
- engine_parsing.py: Engine-specific parsing (EngineParsingHelpers class)
- constructor_parsing.py: Constructor-specific parsing (ConstructorParsingHelpers class)
- results_parsing.py: Race results and points parsing (ResultsParsingHelpers class)

This file now primarily re-exports those functions for backward compatibility.
New code should use the helper classes directly for better organization.

Example:
    # Old way (still works)
    from scrapers.base.table.columns.helpers import extract_driver
    
    # New way (preferred)
    from scrapers.base.table.columns.helpers.driver_parsing import DriverParsingHelpers
    result = DriverParsingHelpers.extract_from_context(ctx, base_url)
"""
import re
from typing import Any
from typing import Optional

from bs4 import Tag

from models.records.link import LinkRecord
from models.services.rounds_service import RoundsService
from scrapers.base.helpers.background import extract_background
from scrapers.base.helpers.cell_splitting import (
    split_cell_on_br_dom_based,
    split_cell_on_br as _split_cell_on_br,
    split_cell_on_br_with_children,
)
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.wiki import is_reference_link
from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.constants import FRACTION_RE
from scrapers.base.table.columns.constants import MARKS_RE
from scrapers.base.table.columns.constants import SPLIT_RESULTS_RE
from scrapers.base.table.columns.context import ColumnContext


def parse_driver_segment(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
    *,
    total_rounds: int | None,
) -> dict[str, Any] | None:
    clean_text = clean_wiki_text(segment.get_text(" ", strip=True))
    if not clean_text:
        return None

    rounds_text = extract_rounds_text(clean_text)
    rounds = (
        RoundsService.parse_rounds(rounds_text, total_rounds=total_rounds)
        if rounds_text
        else []
    )
    number = extract_number(clean_text)

    driver = extract_driver(segment, link_lookup, clean_text)
    if not driver:
        return None

    record: dict[str, Any] = {"driver": driver}
    if number is not None:
        record["no"] = number
    if rounds_text or rounds:
        record["rounds"] = rounds
    return record


def extract_driver(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
    clean_text: str,
) -> dict[str, str | None] | None:
    cleaned = strip_rounds_and_number(clean_text)
    candidates: list[tuple[str, dict[str, str | None]]] = []
    for a in segment.find_all("a", href=True):
        if is_reference_link(a, allow_local_anchors=True):
            continue
        if a.find_parent(class_="flagicon") is not None:
            continue
        text = clean_wiki_text(a.get_text(strip=True))
        if not text:
            continue
        matched = link_lookup.get(text)
        if matched:
            candidates.append((text, matched[0]))
        else:
            candidates.append((text, {"text": text, "url": None}))

    if cleaned and candidates:
        best_match: tuple[str, dict[str, str | None]] | None = None
        for text, link in candidates:
            if text in cleaned:
                if best_match is None or len(text) > len(best_match[0]):
                    best_match = (text, link)
        if best_match:
            return best_match[1]

    if candidates:
        return candidates[-1][1]

    if cleaned:
        return {"text": cleaned, "url": None}
    return None


def extract_rounds_text(text: str) -> str | None:
    match = re.search(r"\\(([^)]+)\\)", text)
    if match:
        return match.group(1).strip()

    match = re.search(r"Rounds?\\s*:?\\s*(.+)$", text, re.I)
    if match:
        return match.group(1).strip()

    return None


def extract_number(text: str) -> int | None:
    match = re.match(r"^\\s*(\\d+)\\b", text)
    if match:
        return int(match.group(1))

    match = re.search(r"\\bNo\\.?\\s*(\\d+)\\b", text, re.I)
    if match:
        return int(match.group(1))

    return None


def strip_rounds_and_number(text: str) -> str:
    cleaned = re.sub(r"\\(([^)]+)\\)", "", text)
    cleaned = re.sub(r"^\\s*\\d+\\b", "", cleaned)
    cleaned = re.sub(r"\\bNo\\.?\\s*\\d+\\b", "", cleaned, flags=re.I)
    cleaned = re.sub(r"Rounds?\\s*:?\\s*.+$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\\s+", " ", cleaned).strip(" -–—")
    return cleaned.strip()


def extract_engine_class(cell: Tag) -> str | None:
    background = extract_background(cell)
    if not background:
        return None
    if is_f2_background(background):
        return "F2"
    return None


def is_f2_background(background: str) -> bool:
    match = re.search(r"#?([0-9a-f]{6}|[0-9a-f]{3})", background, re.I)
    if not match:
        return False
    value = match.group(1).lower()
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    return value == "ffcccc"



def build_driver_link_lookup(links: list[dict[str, str | None]]) -> dict[str, list[dict[str, str | None]]]:
    """Build lookup dictionary for driver/entrant links."""
    lookup: dict[str, list[dict[str, str | None]]] = {}
    for link in links:
        text = link.get("text")
        if not text:
            continue
        key = text.strip().lower()
        if key not in lookup:
            lookup[key] = []
        lookup[key].append(link)
    return lookup


def build_engine_link_lookup(links: list[LinkRecord]) -> dict[str, list[LinkRecord]]:
    lookup: dict[str, list[LinkRecord]] = {}
    for link in normalize_links(links, strip_marks=True, drop_empty=True):
        text = link.get("text") or ""
        if not text:
            continue
        lookup.setdefault(text, []).append(link)
    return lookup


def parse_engine_segment(
    segment: Tag, link_lookup: dict[str, list[LinkRecord]]
) -> dict[str, Any] | None:
    raw_links: list[LinkRecord] = []
    for a in segment.find_all("a", href=True):
        text = clean_wiki_text(a.get_text(strip=True))
        if not text:
            continue
        candidates = link_lookup.get(text)
        if candidates:
            raw_links.append(candidates[0])
        else:
            raw_links.append({"text": text, "url": None})

    links = normalize_links(raw_links, strip_marks=True, drop_empty=True)
    clean_text = clean_wiki_text(segment.get_text(" ", strip=True))
    if not links and not clean_text:
        return None

    model: LinkRecord | None = links[0] if links else None

    displacement = extract_displacement(clean_text)
    type_text = extract_type_text(clean_text, displacement)
    supercharged = extract_supercharged(clean_text)
    turbocharged = extract_turbocharged(clean_text)
    gas_turbine = extract_gas_turbine(clean_text)
    layout, cylinders = parse_engine_type(type_text)
    model_text = extract_model_text(
        clean_text,
        type_text=type_text,
        supercharged=supercharged,
        turbocharged=turbocharged,
        gas_turbine=gas_turbine,
        displacement=displacement,
    )
    if model and model_text:
        model = {**model, "text": model_text}

    data: dict[str, Any] = {}
    if model:
        data["model"] = model
    if displacement:
        data["displacement_l"] = displacement
    if type_text:
        data["type"] = type_text
    if layout:
        data["layout"] = layout
    if cylinders is not None:
        data["cylinders"] = cylinders
    if supercharged:
        data["supercharged"] = True
    if turbocharged:
        data["turbocharged"] = True
    if gas_turbine:
        data["gas_turbine"] = True
    return data or None


def extract_displacement(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:L|litre|liter)s?\b", text, re.I)
    if not match:
        match = re.search(r"\b(\d+(?:\.\d+))\b", text)
        if not match:
            return None
    try:
        value = float(match.group(1))
        if value <= 0 or value > 10:
            return None
        return value
    except ValueError:
        return None


def extract_type_text(text: str, displacement: float | None) -> str | None:
    if not text:
        return None
    cleaned = text
    cleaned = re.sub(
        r"(\d+(?:\.\d+)?)\s*(?:L|litre|liter)s?\b", "", cleaned, flags=re.I
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    match = re.search(
        r"\b(?:V\d{1,2}|W\d{1,2}|I\d{1,2}|L\d{1,2}|H\d{1,2}|F(?:4|6|8|10|12)|Flat[-\s]?\d{1,2}|Straight[-\s]?\d{1,2}|Inline[-\s]?\d{1,2})\b",
        cleaned,
        re.I,
    )
    if match:
        raw = match.group(0)
        normalized = raw.replace(" ", "").replace("-", "")
        lowered = normalized.lower()
        if lowered.startswith(("straight", "inline")):
            digits = re.search(r"\d{1,2}", normalized)
            if digits:
                return f"L{digits.group(0)}"
        return normalized

    if displacement is None:
        match = re.search(r"\bV\d{1,2}\b", text, re.I)
        if match:
            return match.group(0)

    return None


def parse_engine_type(type_text: str | None) -> tuple[str | None, int | None]:
    if not type_text:
        return None, None
    normalized = type_text.replace(" ", "").replace("-", "")
    match = re.match(r"([A-Za-z]+)(\d{1,2})$", normalized)
    if not match:
        return None, None
    layout = match.group(1).upper()
    if layout in {"STRAIGHT", "INLINE", "I", "L"}:
        layout = "L"
    try:
        cylinders = int(match.group(2))
    except ValueError:
        cylinders = None
    return layout, cylinders


def extract_supercharged(text: str) -> bool | None:
    if not text:
        return None
    if re.search(r"\b(supercharger|supercharged)\b", text, re.I):
        return True
    stripped = text.strip()
    if re.search(r"(?:^|\s)s$", stripped, re.I):
        return True
    return None


def extract_turbocharged(text: str) -> bool | None:
    if not text:
        return None
    if re.search(r"\b(turbo|turbocharged)\b", text, re.I):
        return True
    stripped = text.strip()
    if re.search(r"(?:^|\s)t$", stripped, re.I):
        return True
    return None


def extract_gas_turbine(text: str) -> bool | None:
    if not text:
        return None
    if re.search(r"\b(gas\s*turbine|turbine)\b", text, re.I):
        return True
    stripped = text.strip()
    if re.search(r"(?:^|\s)tbn$", stripped, re.I):
        return True
    return None


def extract_model_text(
    text: str,
    *,
    type_text: str | None,
    supercharged: bool | None,
    turbocharged: bool | None,
    gas_turbine: bool | None,
    displacement: float | None,
) -> str | None:
    if not text:
        return None
    cleaned = text
    cleaned = re.sub(
        r"(\d+(?:\.\d+)?)\s*(?:L|litre|liter)s?\b", "", cleaned, flags=re.I
    )
    cleaned = re.sub(
        r"\b(?:V\d{1,2}|W\d{1,2}|I\d{1,2}|L\d{1,2}|H\d{1,2}|F(?:4|6|8|10|12)|Flat[-\s]?\d{1,2}|Straight[-\s]?\d{1,2}|Inline[-\s]?\d{1,2})\b",
        "",
        cleaned,
        flags=re.I,
    )
    if type_text:
        normalized_type = re.escape(type_text)
        cleaned = re.sub(normalized_type, "", cleaned, flags=re.I)
    if supercharged:
        cleaned = re.sub(r"\b(supercharger|supercharged)\b", "", cleaned, flags=re.I)
        cleaned = re.sub(r"(?:^|\s)s$", "", cleaned, flags=re.I)
    if turbocharged:
        cleaned = re.sub(r"\b(turbo|turbocharged)\b", "", cleaned, flags=re.I)
        cleaned = re.sub(r"(?:^|\s)t$", "", cleaned, flags=re.I)
    if gas_turbine:
        cleaned = re.sub(r"\b(gas\s*turbine|turbine)\b", "", cleaned, flags=re.I)
        cleaned = re.sub(r"(?:^|\s)tbn$", "", cleaned, flags=re.I)
    if displacement is not None:
        cleaned = re.sub(rf"\b{re.escape(str(displacement))}\b", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None


def parse_entrant_segment(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
) -> dict[str, Any] | None:
    license_info = extract_licenses(segment, link_lookup)
    strip_refs(segment)

    name = clean_wiki_text(segment.get_text(" ", strip=True))
    if not name:
        return None

    sponsors: list[dict[str, str | None]] = []
    for a in segment.find_all("a", href=True):
        if is_reference_link(a, allow_local_anchors=True):
            continue
        text = clean_wiki_text(a.get_text(strip=True))
        if not text:
            continue
        candidates = link_lookup.get(text)
        if candidates:
            sponsors.append(candidates[0])
        else:
            sponsors.append({"text": text, "url": None})

    record: dict[str, Any] = {"name": name, "title_sponsors": sponsors}
    if license_info is not None:
        record["license"] = license_info
    return record


def extract_licenses(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
) -> dict[str, str | None] | None:
    licenses: list[dict[str, str | None]] = []
    for node in segment.select(".flagicon"):
        for a in node.find_all("a", href=True):
            text = clean_wiki_text(a.get_text(strip=True))
            if not text:
                continue
            candidates = link_lookup.get(text)
            if candidates:
                licenses.append(candidates[0])
            else:
                licenses.append({"text": text, "url": a.get("href")})
            break
        node.decompose()

    if not licenses:
        return None

    license_text = " / ".join(link.get("text") or "" for link in licenses).strip()
    license_url = " / ".join(
        link.get("url") or "" for link in licenses if link.get("url") is not None
    ).strip()
    return {
        "text": license_text,
        "url": license_url or None,
    }


def strip_refs(segment: Tag) -> None:
    for sup in segment.find_all("sup", class_="reference"):
        sup.decompose()


def parse_points_value(text: str):
    if not text:
        return None

    match = FRACTION_RE.search(text)
    if match:
        whole = int(match.group(1)) if match.group(1) else 0
        numerator = int(match.group(2))
        denominator = int(match.group(3))
        if denominator == 0:
            return None
        return whole + numerator / denominator

    return parse_float_from_text(text)


def parse_results(text: str) -> list[dict[str, Any]]:
    parts = SPLIT_RESULTS_RE.split(text)
    results: list[dict[str, Any]] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        marks = MARKS_RE.findall(part)
        cleaned = strip_marks(part) or ""
        cleaned = cleaned.strip()
        value: int | str | None
        if not cleaned or cleaned == "-":
            value = None
        elif cleaned.isdigit():
            value = int(cleaned)
        else:
            value = cleaned
        results.append(
            {
                "value": value,
                "marks": marks or None,
            }
        )
    return results


def parse_superscripts(ctx: ColumnContext) -> tuple[int | None, bool, bool]:
    cell = ctx.cell
    if cell is None:
        return None, False, False

    sup_texts = []
    for sup in cell.find_all("sup"):
        sup_text = clean_wiki_text(sup.get_text(" ", strip=True))
        if sup_text:
            sup_texts.append(sup_text)

    sprint_position = None
    pole_position = False
    fastest_lap = False

    for token in " ".join(sup_texts).split():
        if token.isdigit() and sprint_position is None:
            sprint_position = int(token)
            continue
        letters = re.findall(r"[A-Za-z]", token)
        for letter in letters:
            upper = letter.upper()
            if upper == "P":
                pole_position = True
            elif upper == "F":
                fastest_lap = True

    if not pole_position and cell.find(["b", "strong"]):
        pole_position = True
    if not fastest_lap and cell.find(["i", "em"]):
        fastest_lap = True

    return sprint_position, pole_position, fastest_lap


def extract_race_result_background(ctx: ColumnContext) -> str | None:
    """Extract background color from a table cell in ColumnContext. Kept for backward compatibility."""
    cell = ctx.cell
    if cell is None:
        return None
    return extract_background(cell)


def has_year(text: str) -> bool:
    return re.search(r"\\b\\d{4}\\b", text) is not None
