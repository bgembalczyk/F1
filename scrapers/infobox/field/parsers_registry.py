from typing import Any
from typing import Iterable

from scrapers.parsers.infobox.field.base import InfoboxFieldParser


class InfoboxFieldRegistry:
    def __init__(
        self,
        *,
        default_parser: InfoboxFieldParser[Any],
    ) -> None:
        self._default_parser = default_parser
        self._parsers_by_label: dict[str, InfoboxFieldParser[Any]] = {}

    def register(
        self,
        *,
        labels: Iterable[str],
        parser: InfoboxFieldParser[Any],
    ) -> None:
        for label in labels:
            self._parsers_by_label[label] = parser

    def parser_for_label(self, label: str | None) -> InfoboxFieldParser[Any]:
        if label is None:
            return self._default_parser
        return self._parsers_by_label.get(label, self._default_parser)

