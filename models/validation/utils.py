from typing import Any
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc)


def coerce_number(
    value: Any,
    type_: type,
    field_name: str,
    *,
    allow_none: bool = False,
):
    if value is None:
        if allow_none:
            return None
        msg = f"Pole {field_name} jest wymagane"
        raise ValueError(msg)
    try:
        number = type_(value)
    except (TypeError, ValueError):
        msg = f"Pole {field_name} musi być liczbą"
        raise ValueError(msg) from None
    if number < 0:
        msg = f"Pole {field_name} nie może być ujemne"
        raise ValueError(msg)
    return number
