from typing import Optional
from typing import TypedDict


class SeasonRefPayload(TypedDict):
    year: int
    url: Optional[str]
