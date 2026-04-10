from typing import Any
from typing import NotRequired
from typing import TypedDict


class TableParsedData(TypedDict):
    headers: list[str]
    rows: list[list[str]]
    raw_rows: list[dict[str, str]]
    rich_rows: NotRequired[list[dict[str, Any]]]
