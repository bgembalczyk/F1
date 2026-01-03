from typing import Any


def normalize_empty(value: Any) -> Any:
    if isinstance(value, str):
        return value if value.strip() else None
    if isinstance(value, list | dict):
        return value if value else None
    return value
