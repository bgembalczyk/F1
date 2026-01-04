from typing import Any, Mapping

from models.validation.utils import is_valid_url


def normalize_link(link: Mapping[str, Any] | None) -> dict[str, Any]:
    data: dict[str, Any] = dict(link or {})
    text = str(data.get("text") or "").strip()
    url = data.get("url")
    if url == "":
        url = None
    return {"text": text, "url": url}


def validate_link(link: Mapping[str, Any] | None, *, field_name: str) -> dict[str, Any]:
    normalized = normalize_link(link)
    url = normalized.get("url")
    if url is not None:
        if not isinstance(url, str) or not is_valid_url(url):
            raise ValueError(f"Pole {field_name} zawiera nieprawidłowy URL")
    return normalized
