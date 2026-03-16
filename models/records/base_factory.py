"""Base record factory with common normalization patterns."""

from collections.abc import Callable
from collections.abc import Mapping
from typing import Any
from typing import TypeVar

from models.mappers.field_aliases import apply_field_aliases
from models.records.field_normalizer import FieldNormalizer

T = TypeVar("T")


class BaseRecordFactory:
    """Base class for record factories with shared normalization utilities."""

    def __init__(self, normalizer: FieldNormalizer | None = None):
        self.normalizer = normalizer or FieldNormalizer()

    def apply_aliases(
        self,
        record: Mapping[str, Any],
        aliases: dict[str, str],
        record_name: str,
    ) -> dict[str, Any]:
        return apply_field_aliases(record, aliases, record_name=record_name)

    def normalize_field(
        self,
        payload: dict[str, Any],
        field_name: str,
        normalizer: Callable[[Any, str], Any],
    ) -> None:
        payload[field_name] = normalizer(payload.get(field_name), field_name)

    def normalize_fields(
        self,
        payload: dict[str, Any],
        field_specs: dict[str, Callable[[Any, str], Any]],
    ) -> None:
        for field_name, normalizer in field_specs.items():
            self.normalize_field(payload, field_name, normalizer)

    def normalize_int_fields(
        self,
        payload: dict[str, Any],
        field_names: list[str],
    ) -> None:
        self.normalize_fields(
            payload,
            {name: self.normalizer.normalize_int for name in field_names},
        )

    def normalize_float_fields(
        self,
        payload: dict[str, Any],
        field_names: list[str],
    ) -> None:
        self.normalize_fields(
            payload,
            {name: self.normalizer.normalize_float for name in field_names},
        )

    def normalize_link_fields(
        self,
        payload: dict[str, Any],
        field_names: list[str],
    ) -> None:
        self.normalize_fields(
            payload,
            {name: self.normalizer.normalize_link for name in field_names},
        )

    def normalize_link_list_fields(
        self,
        payload: dict[str, Any],
        field_names: list[str],
    ) -> None:
        self.normalize_fields(
            payload,
            {name: self.normalizer.normalize_link_list for name in field_names},
        )

    def normalize_seasons_fields(
        self,
        payload: dict[str, Any],
        field_names: list[str],
    ) -> None:
        for field_name in field_names:
            payload[field_name] = self.normalizer.normalize_seasons(
                payload.get(field_name),
            )

    def normalize_string_field(self, payload: dict[str, Any], field_name: str) -> None:
        payload[field_name] = self.normalizer.normalize_string(payload.get(field_name))

    def set_defaults(self, payload: dict[str, Any], defaults: dict[str, Any]) -> None:
        for key, default_value in defaults.items():
            payload.setdefault(key, default_value)
