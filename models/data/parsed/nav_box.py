from typing import TypedDict

from models.category.link_item import CategoryLinkItem


class NavBoxParsedData(TypedDict):
    title: str | None
    links: list[CategoryLinkItem]
