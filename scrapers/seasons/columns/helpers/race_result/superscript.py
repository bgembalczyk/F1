from dataclasses import dataclass


@dataclass(frozen=True)
class SuperscriptParseResult:
    sprint_position: int | None
    pole_position: bool
    fastest_lap: bool
    footnotes: list[str]
