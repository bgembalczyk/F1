import re

from models.domain_utils.years import expand_inclusive_range
from models.domain_utils.years import parse_numeric_dash_range
from models.services.helpers import expand_all
from models.services.helpers import unique_sorted
from models.value_objects.rounds import Rounds


def parse_rounds(text: str | None, *, total_rounds: int | None = None) -> Rounds:
    if not text:
        return Rounds()

    normalized = text.strip()
    if not normalized:
        return Rounds()

    lower = normalized.lower()
    if "all" in lower:
        return Rounds.from_values(expand_all(total_rounds))

    normalized = re.sub(
        r"\b(rounds?|races?)\b",
        "",
        normalized,
        flags=re.IGNORECASE,
    )
    parts = [p.strip() for p in re.split(r"[;,]", normalized) if p.strip()]

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

        match = re.search(r"\d+", part)
        if match:
            values.append(int(match.group(0)))

    return Rounds.from_values(unique_sorted(values))
