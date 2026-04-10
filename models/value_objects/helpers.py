from typing import Any
from typing import Mapping
from urllib.parse import urlparse

from models.domain_utils.field_normalization.links import normalize_link_payload


def normalize_iso(value: Any) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    return normalize_text(value)


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

def validate_link(link: Mapping[str, Any] | None, *, field_name: str) -> dict[str, Any]:
    normalized = normalize_link_payload(link)
    url = normalized.get("url")
    if url is not None:
        if not isinstance(url, str) or not is_valid_url(url):
            msg = f"Pole {field_name} zawiera nieprawidłowy URL"
            raise ValueError(msg)
    return normalized


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc)

def normalize_seconds(value: Any) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None
    return None
