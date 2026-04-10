from typing import Any
from typing import TypedDict


class RichCellData(TypedDict):
    text: str
    links: list[dict[str, Any]]
    background: str | None
