from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuleContext:
    record: dict[str, Any]
    source: str
    gp_names: list[str]
    driver_names: list[str]
    car_names: list[str]
    engine_names: list[str]
    non_year_links: list[dict[str, Any]]
    other_links: list[dict[str, Any]]

