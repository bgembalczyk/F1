from typing import Any
from typing import Protocol

from scrapers.seasons.columns_seasons.helpers.race_result.rules.context import ResultRuleContext


class ResultRule(Protocol):
    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None: ...


__all__ = ["ResultRule"]
