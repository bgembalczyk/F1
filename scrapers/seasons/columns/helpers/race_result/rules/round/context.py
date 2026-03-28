from dataclasses import dataclass


@dataclass(frozen=True)
class RoundRuleContext:
    season_year: int | None
    marks: list[str]
    header_text: str
    round_url: str
