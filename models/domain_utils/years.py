import re
from collections.abc import Iterable

SHORT_YEAR_DIGITS = 2
YEAR_PATTERN = re.compile(r"^\d{4}$")
YEAR_RANGE_PATTERN = re.compile(r"^(\d{4})\s*[\-\u2013\u2014]\s*(\d{2,4}|present)$", re.IGNORECASE)
YEAR_TO_PATTERN = re.compile(r"^(\d{4})\s+to\s+(\d{2,4}|present)$", re.IGNORECASE)
ONWARDS_PATTERN = re.compile(r"(\d{4})\s+onward(?:s)?\b", re.IGNORECASE)
PRESENT_PATTERN = re.compile(r"\bpresent\b", re.IGNORECASE)



NUMERIC_DASH_RANGE_PATTERN = re.compile(r"^(\d+)\s*[\-\u2013\u2014]\s*(\d+)$")


def parse_numeric_dash_range(text: str) -> tuple[int, int] | None:
    match = NUMERIC_DASH_RANGE_PATTERN.fullmatch(text.strip())
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2))
    if end < start:
        start, end = end, start
    return start, end

def expand_inclusive_range(start: int, end: int) -> Iterable[int]:
    if end < start:
        start, end = end, start
    return range(start, end + 1)


def normalize_year_text(text: str, current_year: int) -> str:
    normalized = ONWARDS_PATTERN.sub(r"\1-present", text)
    return PRESENT_PATTERN.sub(str(current_year), normalized)


def parse_single_year(text: str) -> int | None:
    value = text.strip()
    return int(value) if YEAR_PATTERN.fullmatch(value) else None


def _expand_short_end_year(start: int, end_text: str) -> int:
    if len(end_text) == SHORT_YEAR_DIGITS:
        return (start // 100) * 100 + int(end_text)
    return int(end_text)


def parse_years_from_part(part: str) -> list[int]:
    value = part.strip()

    for pattern in (YEAR_RANGE_PATTERN, YEAR_TO_PATTERN):
        match = pattern.fullmatch(value)
        if not match:
            continue
        start = int(match.group(1))
        end_text = match.group(2).lower()
        if end_text == "present":
            return [start]
        end = _expand_short_end_year(start, end_text)
        return list(expand_inclusive_range(start, end))

    single = parse_single_year(value)
    return [single] if single is not None else []


def extract_years(text: str, *, current_year: int) -> list[int]:
    normalized_text = normalize_year_text(text, current_year)
    parts = [part.strip() for part in normalized_text.split(",") if part.strip()]

    years: list[int] = []
    seen: set[int] = set()
    for part in parts:
        for year in parse_years_from_part(part):
            if year in seen:
                continue
            seen.add(year)
            years.append(year)
    return years


def parse_year_range(text: str | None) -> dict[str, int | None]:
    normalized = (text or "").strip()
    if not normalized:
        return {"start": None, "end": None}

    onward_match = re.search(r"\b(\d{4})\s+onward(?:s)?\b", normalized, re.IGNORECASE)
    if onward_match:
        return {"start": int(onward_match.group(1)), "end": None}

    range_match = re.search(
        r"\b(\d{4})\s*[\-\u2013\u2014]\s*(\d{2,4}|present)\b",
        normalized,
        re.IGNORECASE,
    )
    if range_match:
        start = int(range_match.group(1))
        end_text = range_match.group(2).lower()
        if end_text == "present":
            return {"start": start, "end": None}
        end = _expand_short_end_year(start, end_text)
        if end < start:
            start, end = end, start
        return {"start": start, "end": end}

    to_match = re.search(
        r"\b(\d{4})\s+to\s+(\d{2,4}|present)\b",
        normalized,
        re.IGNORECASE,
    )
    if to_match:
        start = int(to_match.group(1))
        end_text = to_match.group(2).lower()
        if end_text == "present":
            return {"start": start, "end": None}
        end = _expand_short_end_year(start, end_text)
        if end < start:
            start, end = end, start
        return {"start": start, "end": end}

    years = [int(value) for value in re.findall(r"\d{4}", normalized)]
    if not years:
        return {"start": None, "end": None}

    start = years[0]
    if "present" in normalized.lower() and len(years) == 1:
        return {"start": start, "end": None}

    end = years[-1] if len(years) > 1 else start
    if end < start:
        start, end = end, start
    return {"start": start, "end": end}
