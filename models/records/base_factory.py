"""Base record factory with common normalization patterns."""

from collections.abc import Callable
from collections.abc import Mapping
from typing import Any
from typing import TypedDict
from typing import Protocol
from typing import TypeVar
from typing import runtime_checkable

from models.mappers.field_aliases import apply_field_aliases
from models.records.field_normalizer import FieldNormalizer

T = TypeVar("T")


class FactorySpec(TypedDict, total=False):
    aliases: dict[str, str]
    record_name: str
    field_normalizers: dict[str, Callable[[Any, str], Any]]
    list_field_normalizers: dict[str, list[str]]
    defaults: dict[str, Any]
    nested_factories: dict[str, "BaseRecordFactory"]




@runtime_checkable
class RecordFactoryProtocol(Protocol[T]):
    """Structural contract for record factories."""

    record_type: str

    def build(self, record: Mapping[str, Any]) -> T: ...


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

    def normalize_bool_field(self, payload: dict[str, Any], field_name: str) -> None:
        payload[field_name] = self.normalizer.normalize_bool(payload.get(field_name))

    def apply_spec(
        self,
        record: Mapping[str, Any],
        spec: FactorySpec,
    ) -> dict[str, Any]:
        aliases = spec.get("aliases")
        if aliases:
            payload = self.apply_aliases(
                record,
                aliases,
                spec.get("record_name", "record"),
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
