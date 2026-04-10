"""Base record factory with common normalization patterns."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Mapping
from typing import Any
from typing import TypeVar

from models.field_normalizer import FieldNormalizer
from models.mappers.field_aliases import apply_field_aliases
from models.records.factories.compat import create_compat
from models.records.factories.helpers import normalize_optional_link_or_string
from models.records.factories.spec import FactorySpec

T = TypeVar("T")


class LinkNormalizationMixin:
    def normalize_link_like_field(
        self,
        payload: dict[str, Any],
        field_name: str,
    ) -> None:
        payload[field_name] = normalize_optional_link_or_string(
            self.normalizer,
            payload.get(field_name),
            field_name,
        )


class SeasonNormalizationMixin:
    def normalize_season_like_field(
        self,
        payload: dict[str, Any],
        field_name: str,
    ) -> None:
        payload[field_name] = self.normalizer.normalize_seasons(payload.get(field_name))


class StatusNormalizationMixin:
    def normalize_status_field(
        self,
        payload: dict[str, Any],
        field_name: str,
        allowed: list[str],
    ) -> None:
        payload[field_name] = self.normalizer.normalize_status(
            payload.get(field_name),
            allowed,
            field_name,
        )


class LocationNormalizationMixin:
    def normalize_location_field(
        self,
        payload: dict[str, Any],
        field_name: str,
    ) -> None:
        payload[field_name] = self.normalizer.normalize_string(payload.get(field_name))


class BaseRecordFactory(
    LinkNormalizationMixin,
    SeasonNormalizationMixin,
    StatusNormalizationMixin,
    LocationNormalizationMixin,
):
    """Base class for record builders.

    How to create a new domain factory:
    1. Subclass ``BaseRecordFactory`` in ``models/records/factories/<domain>_factory.py``.
    2. Set ``record_type`` to the registry key for that domain.
    3. Decorate the class with ``@register_factory()``.
    4. Implement only ``build(record)`` as the canonical public entrypoint.
    5. Reuse ``apply_spec`` / normalize helpers for field-level normalization.
    """

    def __init__(self, normalizer: FieldNormalizer | None = None):
        self.normalizer = normalizer or FieldNormalizer()

    @abstractmethod
    def build(self, record: Mapping[str, Any]) -> Any:
        """Build normalized record object from source mapping."""

    def create(self, payload: Mapping[str, Any]) -> Any:
        """Deprecated compatibility adapter for ``build(record)``."""
        return create_compat(payload, self.build)

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
            {f: self.normalizer.normalize_int for f in field_names if f in payload},
        )

    def normalize_float_fields(
        self,
        payload: dict[str, Any],
        field_names: list[str],
    ) -> None:
        self.normalize_fields(
            payload,
            {f: self.normalizer.normalize_float for f in field_names if f in payload},
        )

    def normalize_link_fields(
        self,
        payload: dict[str, Any],
        field_names: list[str],
    ) -> None:
        self.normalize_fields(
            payload,
            dict.fromkeys(field_names, self.normalizer.normalize_link),
        )

    def normalize_link_list_fields(
        self,
        payload: dict[str, Any],
        field_names: list[str],
    ) -> None:
        self.normalize_fields(
            payload,
            dict.fromkeys(field_names, self.normalizer.normalize_link_list),
        )

    def normalize_seasons_fields(
        self,
        payload: dict[str, Any],
        field_names: list[str],
    ) -> None:
        for field_name in field_names:
            self.normalize_season_like_field(payload, field_name)

    def normalize_string_field(self, payload: dict[str, Any], field_name: str) -> None:
        payload[field_name] = self.normalizer.normalize_string(payload.get(field_name))

    def set_defaults(self, payload: dict[str, Any], defaults: dict[str, Any]) -> None:
        for key, default_value in defaults.items():
            payload.setdefault(key, default_value)

    def normalize_bool_field(self, payload: dict[str, Any], field_name: str) -> None:
        payload[field_name] = bool(payload.get(field_name))

    def apply_spec(
        self,
        record: Mapping[str, Any],
        spec: FactorySpec,
    ) -> dict[str, Any]:
        aliases = spec.get("aliases")
        if aliases:
            payload = apply_field_aliases(
                record,
                aliases,
                record_name=spec.get("record_name", "record"),
            )
        else:
            payload = dict(record)

        self.normalize_fields(payload, spec.get("field_normalizers", {}))

        for normalizer_name, field_names in spec.get(
            "list_field_normalizers",
            {},
        ).items():
            method = getattr(self, f"normalize_{normalizer_name}_fields")
            method(payload, field_names)

        for field_name, nested_factory in spec.get("nested_factories", {}).items():
            nested_payload = payload.get(field_name)
            if nested_payload is not None:
                payload[field_name] = nested_factory.build(nested_payload)  # type: ignore[arg-type]

        self.set_defaults(payload, spec.get("defaults", {}))
        return payload
