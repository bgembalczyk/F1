import re
from collections.abc import Iterable
from typing import Any

from models.value_objects.normalized_date import NormalizedDate
from models.value_objects.time_types import DateValue


def split_delimited_text(text: str | None, *, pattern: str = r"[,;/]") -> list[str]:
    if not text:
        return []
    return [part.strip() for part in re.split(pattern, text) if part.strip()]


def parse_int_values(text: str | None) -> list[int]:
    if not text:
        return []
    return [int(value) for value in re.findall(r"\d+", text)]


def expand_all(total_rounds: int | None) -> list[int]:
    if total_rounds is None or total_rounds <= 0:
        return []
    return list(range(1, total_rounds + 1))


def unique_sorted(values: Iterable[int]) -> list[int]:
    seen = set(values)
    return sorted(seen)


def normalize_date_value(rec: dict[str, Any]) -> None:
    """Zamienia date dict na wartość "YYYY-MM-DD" lub "YYYY-MM" lub "YYYY"."""
    d = rec.get("date")
    if not isinstance(d, dict) and not isinstance(d, DateValue | NormalizedDate):
        return
    if isinstance(d, DateValue):
        iso = d.iso
        text = d.raw
    elif isinstance(d, NormalizedDate):
        iso = d.iso
        text = d.text
    else:
        iso = d.get("iso")
        text = d.get("text") or d.get("raw")
    if isinstance(iso, list):
        rec["date"] = iso[0] if iso else None
        return
    if iso:
        rec["date"] = iso
        return

    rec["date"] = text.strip() if isinstance(text, str) and text.strip() else None


def prune_empty(
    obj: Any,
    *,
    drop_empty_lists: bool = True,
    drop_none: bool = True,
    drop_empty_dicts: bool = True,
    drop_url_none: bool = False,
) -> Any:
    if isinstance(obj, dict):
        cleaned: dict[str, Any] = {}
        for key, value in obj.items():
            if drop_url_none and key == "url" and value is None:
                continue
            pruned = prune_empty(
                value,
                drop_empty_lists=drop_empty_lists,
                drop_none=drop_none,
                drop_empty_dicts=drop_empty_dicts,
                drop_url_none=drop_url_none,
            )
            if should_skip(
                pruned,
                drop_none=drop_none,
                drop_empty_lists=drop_empty_lists,
                drop_empty_dicts=drop_empty_dicts,
            ):
                continue
            cleaned[key] = pruned
        return cleaned

    if isinstance(obj, list):
        cleaned_list: list[Any] = []
        for item in obj:
            pruned = prune_empty(
                item,
                drop_empty_lists=drop_empty_lists,
                drop_none=drop_none,
                drop_empty_dicts=drop_empty_dicts,
                drop_url_none=drop_url_none,
            )
            if should_skip(
                pruned,
                drop_none=drop_none,
                drop_empty_lists=drop_empty_lists,
                drop_empty_dicts=drop_empty_dicts,
            ):
                continue
            cleaned_list.append(pruned)
        return cleaned_list

    return obj


def should_skip(
    value: Any,
    *,
    drop_none: bool = True,
    drop_empty_lists: bool = True,
    drop_empty_dicts: bool = True,
) -> bool:
    """
    Sprawdza, czy wartość powinna zostać pominięta w pruning'u.

    Args:
        value: Wartość do sprawdzenia
        drop_none: Pominąć None
        drop_empty_lists: Pominąć puste listy
        drop_empty_dicts: Pominąć puste słowniki

    Returns:
        True jeśli wartość powinna zostać pominięta
    """
    if drop_none and value is None:
        return True
    if drop_empty_lists and isinstance(value, list) and len(value) == 0:
        return True
    return bool(drop_empty_dicts and isinstance(value, dict) and len(value) == 0)
