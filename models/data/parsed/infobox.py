from typing import Any
from typing import TypedDict


class InfoboxParsedData(TypedDict):
    title: str | None
    rows: dict[str, Any]
