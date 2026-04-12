from typing import Any
from typing import TypedDict


class WikiInfoboxData(TypedDict):
    title: str | None
    rows: dict[str, Any]
