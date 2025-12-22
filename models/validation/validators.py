from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional
from urllib.parse import urlparse

from models.value_objects import Link, SeasonRef
from models.serializers import to_dict_any


def _coerce_number(value: Any, type_: type, field_name: str):
    if value is None:
        return None
    try:
        number = type_(value)
    except (TypeError, ValueError):
        raise ValueError(f"Pole {field_name} musi być liczbą") from None
    if number < 0:
        raise ValueError(f"Pole {field_name} nie może być ujemne")
    return number


def validate_int(value: Any, field_name: str) -> Optional[int]:
    return _coerce_number(value, int, field_name)


def validate_float(value: Any, field_name: str) -> Optional[float]:
    return _coerce_number(value, float, field_name)


def _is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc)


def validate_link(
    link: Dict[str, Any] | Link | None, *, field_name: str
) -> Dict[str, Any]:
    """
    Normalizuje link do postaci dict: {"text": str, "url": Optional[str]}.

    Akceptuje:
    - Link (value object) -> waliduje przez Link i zwraca jego dict,
    - dict -> waliduje text/url (w tym URL), a potem przepuszcza przez Link.from_dict
             (żeby mieć jedno źródło prawdy dla normalizacji).
    """
    if isinstance(link, Link):
        return link.to_dict()

    data: Dict[str, Any] = dict(link or {})
    text = str(data.get("text") or "").strip()
    url = data.get("url")

    if url is not None and url != "":
        if not isinstance(url, str) or not _is_valid_url(url):
            raise ValueError(f"Pole {field_name} zawiera nieprawidłowy URL")
    else:
        url = None

    try:
        parsed = Link.from_dict({"text": text, "url": url})
    except ValueError as exc:
        # utrzymujemy komunikat z pliku 1, ale oparty o pre-check z pliku 2
        raise ValueError(f"Pole {field_name} zawiera nieprawidłowy URL") from exc

    return parsed.to_dict()


def validate_links(
    links: Iterable[Dict[str, Any] | Link] | None, *, field_name: str
) -> list[Dict[str, Any]]:
    result: list[Dict[str, Any]] = []
    for link in links or []:
        validated = validate_link(link, field_name=field_name)
        if validated.get("text") or validated.get("url") is not None:
            result.append(validated)
    return result


def validate_seasons(
    seasons: Iterable[Dict[str, Any] | SeasonRef] | None,
) -> list[Dict[str, Any]]:
    """
    Normalizuje sezony do listy dictów.

    Akceptuje:
    - SeasonRef -> to_dict(),
    - dict -> próbuje SeasonRef.from_dict(item) (jak plik 1),
             a jeśli to się nie uda, fallback na prostą walidację {year,url} (jak plik 2).
    """
    result: list[Dict[str, Any]] = []

    for item in seasons or []:
        if item is None:
            continue

        # 1) VO
        if isinstance(item, SeasonRef):
            season = item
            season_dict = season.to_dict()
            if season_dict is not None:
                result.append(season_dict)
            continue

        # 2) próba przez SeasonRef (źródło prawdy jeśli to jest kompatybilny dict)
        try:
            season = SeasonRef.from_dict(item)
        except (ValueError, TypeError):
            season = None

        if season is not None:
            season_dict = season.to_dict()
            if season_dict is not None:
                result.append(season_dict)
            continue

        # 3) fallback: minimalny schemat {year,url}
        if not isinstance(item, dict):
            continue

        year = item.get("year")
        if year is None:
            continue

        year_int = validate_int(year, "year")
        if year_int is None:
            continue

        validated: Dict[str, Any] = {"year": year_int}

        url = item.get("url")
        if url:
            if not isinstance(url, str) or not _is_valid_url(url):
                raise ValueError("Pole seasons zawiera nieprawidłowy URL")
            validated["url"] = url

        result.append(validated)

    return result


def validate_status(value: Any, allowed: Iterable[str], field_name: str) -> str:
    status_normalized = (value or "").strip().lower()
    allowed_normalized: list[str] = []
    allowed_set: set[str] = set()
    for option in allowed:
        normalized = str(option).strip().lower()
        if normalized and normalized not in allowed_set:
            allowed_set.add(normalized)
            allowed_normalized.append(normalized)
    if status_normalized not in allowed_set:
        allowed_display = ", ".join(allowed_normalized)
        raise ValueError(
            f"Pole {field_name} musi mieć jedną z wartości: {allowed_display}"
        )
    return status_normalized


def model_to_dict(
    model: Any,
    *,
    logger: logging.Logger | logging.LoggerAdapter | None = None,
) -> Dict[str, Any]:
    result = to_dict_any(model, logger=logger)
    if not isinstance(result, dict):
        raise TypeError("Nieobsługiwany typ modelu")
    return result


def normalize_link_list(
    items: list[Link | Dict[str, Any]] | None,
) -> list[Link]:
    """
    Normalizuje listę Link | dict -> list[Link], filtrując puste linki.

    Używane w Circuit.grands_prix i EngineManufacturer.engines_built_in.
    """
    if not items:
        return []

    result: list[Link] = []
    for item in items:
        link = item if isinstance(item, Link) else Link.from_dict(item)
        if not link.is_empty():
            result.append(link)

    return result


def normalize_season_list(
    items: list[SeasonRef | Dict[str, Any]] | None,
) -> list[SeasonRef]:
    """
    Normalizuje listę SeasonRef | dict -> list[SeasonRef], filtrując None.

    Używane w Circuit.seasons i EngineManufacturer.seasons.
    """
    if not items:
        return []

    result: list[SeasonRef] = []
    for item in items:
        season = item if isinstance(item, SeasonRef) else SeasonRef.from_dict(item)
        if season is not None:
            result.append(season)

    return result
