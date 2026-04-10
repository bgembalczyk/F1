from typing import Any

from scrapers.constructors_constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_NAME_HEADER
from scrapers.wiki.parsers.elements.wiki_table import WikiTableBaseParser


class FormerConstructorsTableParser(WikiTableBaseParser):
    table_type = "former_constructors"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        del table_data
        expected = {
            CONSTRUCTOR_NAME_HEADER.lower(),
            CONSTRUCTOR_LICENSED_IN_HEADER.lower(),
            CONSTRUCTOR_SEASONS_HEADER.lower(),
        }
        normalized = {header.strip().lower() for header in headers}
        return expected.issubset(normalized)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {header: header.strip().lower().replace(" ", "_") for header in headers}
