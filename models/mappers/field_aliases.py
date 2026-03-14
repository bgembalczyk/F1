from collections.abc import Mapping
from typing import Any

FIELD_ALIASES: dict[str, dict[str, str]] = {
    "constructor": {
        "wcc": "wcc_titles",
        "wdc": "wdc_titles",
    },
    "driver": {
        "entries": "race_entries",
        "starts": "race_starts",
        "poles": "pole_positions",
    },
}


def apply_field_aliases(
    record: Mapping[str, Any],
    aliases: Mapping[str, str],
    *,
    record_name: str,
) -> dict[str, Any]:
    normalized = dict(record)
    conflicts: list[tuple[str, str]] = []

    for alias, target in aliases.items():
        if alias not in normalized:
            continue
        if target in normalized:
            conflicts.append((alias, target))
            continue
        normalized[target] = normalized.pop(alias)

    if conflicts:
        conflict_details = ", ".join(
            f"{alias}->{target}" for alias, target in conflicts
        )
        raise ValueError(f"Konflikt aliasów dla {record_name}: {conflict_details}")

    return normalized
