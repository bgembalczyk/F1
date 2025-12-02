from typing import Protocol, Any, Dict

from scrapers.helpers.columns.column_context import ColumnContext
from scrapers.helpers.columns.columns import (
    AutoColumn,
    SkipColumn,
    TextColumn,
    ListColumn,
    SeasonsColumn,
    UrlColumn,
    LinksListColumn,
    IntColumn,
    FloatColumn,
)


class ColumnType(Protocol):
    def parse(self, ctx: ColumnContext) -> Any: ...


class ColumnTypeRegistry:
    """
    Prosty rejestr:
    nazwa typu (string) -> instancja klasy kolumny.
    """

    def __init__(self) -> None:
        self._types: Dict[str, ColumnType] = {
            "auto": AutoColumn(),
            "skip": SkipColumn(),
            "text": TextColumn(),
            "list": ListColumn(),
            "seasons": SeasonsColumn(),
            "link": UrlColumn(),
            "list_of_links": LinksListColumn(),
            "int": IntColumn(),
            "float": FloatColumn(),
        }

    def get(self, name: str) -> ColumnType:
        return self._types.get(name, self._types["auto"])
