from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from models.domain_utils.normalization import normalize_link_item
from models.domain_utils.normalization import normalize_link_items
from models.domain_utils.normalization import normalize_season_items
from models.validation.helpers import validate_status
from models.validation.utils import coerce_number

if TYPE_CHECKING:
    from models.records.link import LinkRecord
    from models.records.season import SeasonRecord
    from models.value_objects.season_ref import SeasonRef


class FieldNormalizer:
    """Service class for normalizing record fields."""

    @staticmethod
    def normalize_int(value: Any, field_name: str) -> int | None:
        if value is None:
            return None
        try:
            return coerce_number(value, int, field_name, allow_none=True)
        except ValueError:
            return None

    @staticmethod
    def normalize_float(value: Any, field_name: str) -> float | None:
        if value is None:
            return None
        try:
            return coerce_number(value, float, field_name, allow_none=True)
        except ValueError:
            return None

    @staticmethod
    def normalize_link(value: Any, field_name: str) -> LinkRecord | None:
        return cast(
            "LinkRecord | None",
            normalize_link_item(value, field_name=field_name),
        )

    @staticmethod
    def normalize_link_list(value: Any, field_name: str) -> list[LinkRecord]:
        items = value if isinstance(value, list) else [value]
        return cast(
            "list[LinkRecord]",
            normalize_link_items(items, field_name=field_name),
        )

    @staticmethod
    def normalize_seasons(value: Any) -> list[SeasonRecord]:
        items: list[SeasonRef | dict[str, Any] | None]
        if value is None:
            items = []
        elif isinstance(value, list):
            items = value
        else:
            items = [value]
        return cast(
            "list[SeasonRecord]",
            [
                season.to_dict()
                for season in normalize_season_items(
                    items,
                    with_default_url=True,
                )
            ],
        )

    @staticmethod
    def normalize_status(
        value: Any,
        allowed: list[str],
        field_name: str,
    ) -> str | None:
        if value is None:
            return None
        try:
            return validate_status(value, allowed, field_name)
        except ValueError:
            return str(value).strip().lower() or None

    @staticmethod
    def normalize_string(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip() or None
        return str(value).strip() or None
