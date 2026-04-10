from typing import TypedDict

from models.types import CategoryLinkItem


class NavBoxParsedData(TypedDict):
    title: str | None
    links: list[CategoryLinkItem]
