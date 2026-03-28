from dataclasses import dataclass


@dataclass(frozen=True)
class ResultRuleContext:
    season_year: int | None
    background: str | None
    footnotes: list[str]
