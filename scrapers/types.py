from collections.abc import Iterable
from collections.abc import Mapping
from typing import Protocol
from typing import TypeAlias
from typing import runtime_checkable

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
MetadataMap: TypeAlias = Mapping[str, object]
PipelineRecord: TypeAlias = dict[str, JsonValue]


@runtime_checkable
class ExportableRecord(Protocol):
    def __getitem__(self, key: str) -> JsonValue: ...

    def keys(self) -> Iterable[str]: ...

    def items(self) -> Iterable[tuple[str, JsonValue]]: ...
