from typing import Any
from typing import Iterable

from scrapers.parsers.infobox.field.protocol import HtmlInfoboxFieldParser


class InfoboxFieldRegistry:
    def __init__(
        self,
        *,
        default_parser: HtmlInfoboxFieldParser[Any],
    ) -> None:
        self._default_parser = default_parser
        self._parsers_by_label: dict[str, HtmlInfoboxFieldParser[Any]] = {}

    def register(
        self,
        *,
        labels: Iterable[str],
        parser: HtmlInfoboxFieldParser[Any],
    ) -> None:
        for label in labels:
            self._parsers_by_label[label] = parser

    def parser_for_label(self, label: str | None) -> HtmlInfoboxFieldParser[Any]:
        if label is None:
            return self._default_parser
        return self._parsers_by_label.get(label, self._default_parser)

