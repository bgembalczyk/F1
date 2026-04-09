from typing import Protocol

from scrapers.columns.context import ColumnContext


class ConstructorPartParser(Protocol):
    def __init__(self, index: int) -> None: ...

    def parse(self, ctx: ColumnContext) -> dict[str, object] | None: ...
