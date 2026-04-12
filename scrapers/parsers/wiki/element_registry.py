from dataclasses import dataclass
from typing import Callable

from bs4 import Tag

from models.data.wiki_parser import WikiParserData
from scrapers.parsers.rules import ParserRule


@dataclass(frozen=True)
class ElementRegistry:
    rules: tuple[ParserRule, ...]

    @staticmethod
    def _get_classes(el: Tag) -> list[str]:
        classes = el.get("class") or []
        if isinstance(classes, str):
            return classes.split()
        return list(classes)

    def resolve(
        self,
        element: Tag,
    ) -> tuple[str, Callable[[Tag], WikiParserData]] | None:
        for rule in self.rules:
            if rule.predicate(element):
                return rule.result_type, rule.parser
        return None

