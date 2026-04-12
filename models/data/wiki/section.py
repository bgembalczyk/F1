from typing import Any
from typing import TypedDict


class WikiSectionData(TypedDict):
    sections: list[dict[str, Any]]
