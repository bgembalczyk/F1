from typing import TypedDict

from models.category.link_item import CategoryLinkItem


class CategoryGroup(TypedDict):
    category: str | None
    links: list[CategoryLinkItem]
