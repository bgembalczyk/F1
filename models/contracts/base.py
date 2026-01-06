from dataclasses import dataclass, field, fields
from typing import Any, Iterator, Mapping, MutableMapping


@dataclass(slots=True)
class DataContract(MutableMapping[str, Any]):
    _extra: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "DataContract":
        field_names = {field.name for field in fields(cls) if field.init}
        field_names.discard("_extra")
        kwargs = {key: value for key, value in record.items() if key in field_names}
        instance = cls(**kwargs)  # type: ignore[arg-type]
        instance._extra.update(
            {key: value for key, value in record.items() if key not in field_names}
        )
        return instance

    def _field_names(self) -> set[str]:
        field_names = {field.name for field in fields(self) if field.init}
        field_names.discard("_extra")
        return field_names

    def to_dict(self) -> dict[str, Any]:
        field_names = self._field_names()
        payload = {name: getattr(self, name) for name in field_names}
        if self._extra:
            payload.update(self._extra)
        return payload

    def __getitem__(self, key: str) -> Any:
        if key in self._field_names():
            return getattr(self, key)
        if key in self._extra:
            return self._extra[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._field_names():
            setattr(self, key, value)
            return
        self._extra[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self._field_names():
            setattr(self, key, None)
            return
        del self._extra[key]

    def __iter__(self) -> Iterator[str]:
        yield from self._field_names()
        yield from self._extra.keys()

    def __len__(self) -> int:
        return len(self._field_names()) + len(self._extra)
