import logging
from typing import Any, Dict, Iterable, Optional

from models.records.link import LinkRecord
from models.serializers import to_dict_any
from models.validation.utils import coerce_number, is_valid_url
from models.value_objects.link import Link
from models.value_objects.season_ref import SeasonRef


def validate_int(value: Any, field_name: str) -> Optional[int]:
    return coerce_number(value, int, field_name, allow_none=True)


def validate_float(value: Any, field_name: str) -> Optional[float]:
    return coerce_number(value, float, field_name, allow_none=True)


def normalize_and_validate_link_dict(
    link: Dict[str, Any] | None, *, field_name: str
) -> LinkRecord | None:
    data: Dict[str, Any] = dict(link or {})
    text = str(data.get("text") or "").strip()
    url = data.get("url")
    if url == "":
        url = None
    if text == "" and url is None:
        return None
    if url is not None:
        if not isinstance(url, str) or not is_valid_url(url):
            raise ValueError(f"Pole {field_name} zawiera nieprawidłowy URL")
    return {"text": text, "url": url}


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

    normalized = normalize_and_validate_link_dict(link, field_name=field_name)
    if normalized is None:
        return {"text": "", "url": None}

    return Link.from_dict(normalized).to_dict()


def validate_links(
    links: Iterable[Dict[str, Any] | Link] | None, *, field_name: str
) -> list[Dict[str, Any]]:
    validated = (validate_link(link, field_name=field_name) for link in links or [])
    return filter_nonempty(validated, key=is_empty_link)


def normalize_season_item(
    item: Dict[str, Any] | SeasonRef | None,
) -> Dict[str, Any] | None:
    """
    Normalizuje jeden element sezonu.

    Akceptuje:
    - None -> None,
    - SeasonRef -> to_dict(),
    - dict -> próbuje SeasonRef.from_dict(item),
             a jeśli to się nie uda, fallback na prostą walidację {year,url}.
    """
    if item is None:
        return None

    # 1) VO
    if isinstance(item, SeasonRef):
        return item.to_dict()

    # 2) próba przez SeasonRef (źródło prawdy jeśli to jest kompatybilny dict)
    try:
        season = SeasonRef.from_dict(item)
    except (ValueError, TypeError):
        season = None

    if season is not None:
        return season.to_dict()

    # 3) fallback: minimalny schemat {year,url}
    if not isinstance(item, dict):
        return None

    year = item.get("year")
    if year is None:
        return None

    year_int = validate_int(year, "year")
    if year_int is None:
        return None

    validated: Dict[str, Any] = {"year": year_int}

    url = item.get("url")
    if url:
        if not isinstance(url, str) or not is_valid_url(url):
            raise ValueError("Pole seasons zawiera nieprawidłowy URL")
        validated["url"] = url

    return validated


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
    normalized = (normalize_season_item(item) for item in seasons or [])
    return filter_nonempty(normalized)


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

    normalized = (
        item if isinstance(item, Link) else Link.from_dict(item) for item in items
    )
    return filter_nonempty(normalized, key=is_empty_link)


def normalize_season_list(
    items: list[SeasonRef | Dict[str, Any]] | None,
) -> list[SeasonRef]:
    """
    Normalizuje listę SeasonRef | dict -> list[SeasonRef], filtrując None.

    Używane w Circuit.seasons i EngineManufacturer.seasons.
    """
    if not items:
        return []

    normalized = (
        item if isinstance(item, SeasonRef) else SeasonRef.from_dict(item)
        for item in items
    )
    return filter_nonempty(normalized)


def is_empty_link(value: Link | Dict[str, Any] | None) -> bool:
    if value is None:
        return True
    if isinstance(value, Link):
        text = value.text
        url = value.url
    else:
        text = str(value.get("text") or "").strip()
        url = value.get("url")
        if url == "":
            url = None
    return text == "" and url is None



def filter_nonempty(items: Iterable[Any] | None, *, key: Any = None) -> list[Any]:
    result: list[Any] = []
    for item in items or []:
        if item is None:
            continue
        if key is not None and key(item):
            continue
        result.append(item)
    return result
