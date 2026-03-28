from typing import Any
from typing import Protocol

from scrapers.seasons.columns.helpers.race_result.rules.context import ResultRuleContext


class ResultRule(Protocol):
    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None: ...
