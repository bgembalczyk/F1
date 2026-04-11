from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from typing import Generic

from scrapers.parsers.infobox.field.protocol import InfoboxFieldParser
from scrapers.parsers.infobox.field.protocol import Input
from scrapers.parsers.infobox.field.protocol import Output


@dataclass(frozen=True)
class CallableInfoboxFieldParser(
    InfoboxFieldParser[Input, Output],
    Generic[Input, Output],
):
    _parser: Callable[[Input], Output]

    def parse(self, value: Input) -> Output:
        return self._parser(value)
