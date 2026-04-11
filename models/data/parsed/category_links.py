from typing import TypedDict

from models.category.group import CategoryGroup


class CategoryLinksParsedData(TypedDict):
    categories: list[CategoryGroup]
