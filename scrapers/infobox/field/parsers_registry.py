from collections.abc import Iterable
from typing import Any

from scrapers.parsers.contracts.infobox_fields import InfoboxHtmlFieldParserABC


class InfoboxFieldRegistry:
    def __init__(
        self,
        *,
        default_parser: InfoboxHtmlFieldParserABC[Any],
    ) -> None:
        self._default_parser = default_parser
        self._parsers_by_label: dict[str, InfoboxHtmlFieldParserABC[Any]] = {}

    def register(
        self,
        *,
        labels: Iterable[str],
        parser: InfoboxHtmlFieldParserABC[Any],
    ) -> None:
        for label in labels:
            self._parsers_by_label[label] = parser

    def parser_for_label(self, label: str | None) -> InfoboxHtmlFieldParserABC[Any]:
        if label is None:
            return self._default_parser
        return self._parsers_by_label.get(label, self._default_parser)
