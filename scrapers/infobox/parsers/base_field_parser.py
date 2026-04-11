from abc import ABC
from typing import Any

from bs4 import Tag

from scrapers.parsers.wiki.base import WikiTagParser


class BaseInfoboxFieldParser(WikiTagParser[Any], ABC):
    """Base contract for infobox field parsers, processing Wikipedia HTML tags."""

    # We do not override `parse(self, raw: Tag) -> Any` here because
    # the interface requires implementation by concrete classes.
    # However, inheriting from `WikiTagParser` ensures `parse` is marked
    # as abstract and required.

__all__ = ["BaseInfoboxFieldParser"]
