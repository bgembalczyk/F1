import re

from models.domain_utils.years import expand_inclusive_range
from models.domain_utils.years import parse_numeric_dash_range
from models.services.helpers import expand_all
from models.services.helpers import unique_sorted
from models.value_objects.rounds import Rounds


_ROUNDS_RE = re.compile(r"\b(rounds?|races?)\b", flags=re.IGNORECASE)
_SPLIT_RE = re.compile(r"[;,]")
_DIGITS_RE = re.compile(r"\d+")


def parse_rounds(text: str | None, *, total_rounds: int | None = None) -> Rounds:
    if not text:
        return Rounds()

    normalized = text.strip()
    if not normalized:
        return Rounds()

    lower = normalized.lower()
    if "all" in lower:
        return Rounds(tuple(expand_all(total_rounds) or ()))

    normalized = _ROUNDS_RE.sub("", normalized)
    parts = [p.strip() for p in _SPLIT_RE.split(normalized) if p.strip()]

    values: list[int] = []
    for part in parts:
        if not part:
            continue

        if "all" in part.lower():
            values.extend(expand_all(total_rounds))
            continue

        parsed_range = parse_numeric_dash_range(part)
        if parsed_range:
            start, end = parsed_range
            values.extend(expand_inclusive_range(start, end))
            continue

        match = _DIGITS_RE.search(part)
        if match:
            values.append(int(match.group(0)))

    return Rounds(tuple(unique_sorted(values) or ()))
