from typing import TypedDict

from models.types import CategoryGroup


class CategoryLinksParsedData(TypedDict):
    categories: list[CategoryGroup]
