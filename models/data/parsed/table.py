from typing import Any
from typing import TypedDict

from typing_extensions import NotRequired


class TableParsedData(TypedDict):
    headers: list[str]
    rows: list[list[str]]
    raw_rows: list[dict[str, str]]
    rich_rows: NotRequired[list[dict[str, Any]]]
