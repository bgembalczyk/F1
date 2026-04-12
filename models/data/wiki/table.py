from typing import Any
from typing import TypedDict


class WikiTableData(TypedDict):
    headers: list[str]
    rows: list[list[str]]
    raw_rows: list[dict[str, str]]
    rich_rows: list[dict[str, Any]]
