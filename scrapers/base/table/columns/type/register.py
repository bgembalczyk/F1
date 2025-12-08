from typing import Dict

from scrapers.base.table.columns.type.protocol import ColumnType
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.float import FloatColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.list import ListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn


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
