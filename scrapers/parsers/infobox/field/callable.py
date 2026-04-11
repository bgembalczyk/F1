from dataclasses import dataclass
from typing import Callable
from typing import Generic

from scrapers.parsers.infobox.field.base import Input
from scrapers.parsers.infobox.field.base import Output


@dataclass(frozen=True)
class CallableInfoboxFieldParser(Generic[Input, Output]):
    _parser: Callable[[Input], Output]

    def parse(self, value: Input) -> Output:
        return self._parser(value)
