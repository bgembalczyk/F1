from __future__ import annotations

from typing import Any
from typing import TypeAlias

from bs4 import BeautifulSoup
from bs4 import Tag

WikiTagInput: TypeAlias = Tag
WikiSoupInput: TypeAlias = BeautifulSoup
WikiDictFragmentInput: TypeAlias = dict[str, Any]
WikiParserInput: TypeAlias = WikiTagInput | WikiSoupInput | WikiDictFragmentInput

INPUT_TYPE_MAP: dict[str, type[Any]] = {
    "tag": Tag,
    "soup": BeautifulSoup,
    "dict_fragment": dict,
}

INPUT_TYPE_TO_CANONICAL: dict[str, str] = {
    "tag": "soup",
    "soup": "soup",
    "dict_fragment": "dict_fragment",
}

__all__ = [
    "INPUT_TYPE_MAP",
    "INPUT_TYPE_TO_CANONICAL",
    "WikiDictFragmentInput",
    "WikiParserInput",
    "WikiSoupInput",
    "WikiTagInput",
]
