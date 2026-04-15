"""Unified base class for all domain models.

Replaces DataContract, ValidatedModel, ValueObject, and *RecordModel with a single
consistent base that handles validation, serialization, and construction uniformly.
"""
from __future__ import annotations

from collections.abc import Iterator
from collections.abc import Mapping
from collections.abc import MutableMapping
from dataclasses import asdict
from dataclasses import field
from dataclasses import fields
from dataclasses import is_dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from typing_extensions import Self

if TYPE_CHECKING:
    from validation.issue import ValidationIssue
    from validation.schemas import RecordSchema


class DomainModel(MutableMapping[str, Any]):
    """Unified base for all domain models.

    Combines the responsibilities of:
    - ``DataContract``  – typed record container with dict-like access
    - ``ValidatedModel`` – schema-based validation via ``__schema__``
    - ``ValueObject``   – serialisation/deserialisation helpers
    - ``*RecordModel``  – raw-dict wrappers with domain-specific helpers
    """

    __schema__: ClassVar[RecordSchema | Mapping[str, Any] | None] = None

    # ------------------------------------------------------------------
    # Validation helpers (formerly ValidatedModel)
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:  # called by dataclass-generated __init__
        self.validate()

    def validate(self) -> None:
        """Override in subclasses to perform field-level validation."""
        return

    @classmethod
    def validate_record(cls, record: Mapping[str, Any]) -> list[ValidationIssue]:
        from validation.issue import ValidationIssue  # noqa: F401
        from validation.record_validation import validate_record as _validate
        schema = cls.__schema__
        if schema is None:
            return []
        return _validate(record, schema)

    @classmethod
    def model_validate(cls, record: Mapping[str, Any]) -> Self:
        errors = cls.validate_record(record)
        if errors:
            details = ", ".join(error.message for error in errors)
            msg = f"{cls.__name__} validation failed: {details}"
            raise ValueError(msg)
        return cls(**dict(record))  # type: ignore[call-arg]

    # ------------------------------------------------------------------
    # Construction helpers (formerly from_record / from_object / from_mapping / from_dict)
    # ------------------------------------------------------------------

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> Self:
        """Construct instance from a mapping, storing unknown keys in ``_extra``."""
        if not is_dataclass(cls):
            return cls(**dict(record))  # type: ignore[call-arg]
        field_names: set[str] = {f.name for f in fields(cls) if f.init}  # type: ignore[arg-type]
        field_names.discard("_extra")
        kwargs = {k: v for k, v in record.items() if k in field_names}
        instance = cls(**kwargs)  # type: ignore[call-arg]
        extra_items = {k: v for k, v in record.items() if k not in field_names}
        if extra_items:
            extra: dict[str, Any] = getattr(instance, "_extra", None)  # type: ignore[assignment]
            if isinstance(extra, dict):
                extra.update(extra_items)
        return instance

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> Self | None:
        """Build instance from a mapping payload (override in subclasses as needed)."""
        return cls.from_record(data)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | Self | None) -> Self | None:
        """Safely build instance from mapping, self-instance, or None."""
        if data is None:
            return None
        if isinstance(data, cls):
            return data
        if not isinstance(data, Mapping):
            msg = f"Nieobsługiwany typ danych: {type(data)!r}"
            raise TypeError(msg)
        try:
            return cls.from_mapping(data)
        except (TypeError, ValueError, KeyError) as exc:
            msg = f"Nie można utworzyć {cls.__name__} z przekazanego payloadu: {exc}"
            raise ValueError(msg) from exc

    @classmethod
    def from_object(cls, value: object) -> Self | None:
        """Construct instance from an arbitrary object (returns None if not a dict)."""
        if not isinstance(value, dict):
            return None
        return cls.from_record(value)

    @classmethod
    def can_handle(cls, record: Mapping[str, Any]) -> bool:
        """Return True if this model can represent the given record (override in subclasses)."""
        del record
        return False

    # ------------------------------------------------------------------
    # Serialisation (formerly to_dict from ValueObject / DataContract)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation of this model."""
        if is_dataclass(self):
            field_names: set[str] = {f.name for f in fields(self) if f.init}  # type: ignore[arg-type]
            field_names.discard("_extra")
            result = {name: getattr(self, name) for name in field_names}
            extra: dict[str, Any] = getattr(self, "_extra", {})
            if extra:
                result.update(extra)
            return result
        msg = f"Nieobsługiwany DomainModel: {type(self)!r}"
        raise TypeError(msg)

    # ------------------------------------------------------------------
    # MutableMapping implementation (formerly DataContract)
    # ------------------------------------------------------------------

    def _field_names(self) -> set[str]:
        if not is_dataclass(self):
            return set()
        result: set[str] = {f.name for f in fields(self) if f.init}  # type: ignore[arg-type]
        result.discard("_extra")
        return result

    def __getitem__(self, key: str) -> Any:
        if key in self._field_names():
            return getattr(self, key)
        extra: dict[str, Any] = getattr(self, "_extra", {})
        if key in extra:
            return extra[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._field_names():
            setattr(self, key, value)
            return
        extra: dict[str, Any] = getattr(self, "_extra", None)  # type: ignore[assignment]
        if isinstance(extra, dict):
            extra[key] = value
        else:
            object.__setattr__(self, key, value)

    def __delitem__(self, key: str) -> None:
        if key in self._field_names():
            setattr(self, key, None)
            return
        extra: dict[str, Any] = getattr(self, "_extra", {})
        del extra[key]

    def __iter__(self) -> Iterator[str]:
        yield from self._field_names()
        extra: dict[str, Any] = getattr(self, "_extra", {})
        yield from extra.keys()

    def __len__(self) -> int:
        extra: dict[str, Any] = getattr(self, "_extra", {})
        return len(self._field_names()) + len(extra)


__all__ = ["DomainModel"]
