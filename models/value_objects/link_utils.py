from collections.abc import Mapping
from typing import Any

from models.domain_utils.field_normalization.links import normalize_link_payload
from models.validation.utils import is_valid_url


def normalize_link(link: Mapping[str, Any] | None) -> dict[str, Any]:
    return normalize_link_payload(link)


def validate_link(link: Mapping[str, Any] | None, *, field_name: str) -> dict[str, Any]:
    normalized = normalize_link(link)
    url = normalized.get("url")
    if url is not None:
        if not isinstance(url, str) or not is_valid_url(url):
            msg = f"Pole {field_name} zawiera nieprawidłowy URL"
            raise ValueError(msg)
    return normalized
