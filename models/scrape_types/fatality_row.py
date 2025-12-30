from typing import Optional, TypedDict

from models.records.link import LinkRecord
from scrapers.base.helpers.value_objects import NormalizedDate


class FatalityRow(TypedDict, total=False):
    driver: LinkRecord
    date: NormalizedDate
    is_formula_two_car: bool
    age: Optional[int]
    event: Optional[str | LinkRecord | list[LinkRecord]]
    event_is_non_championship: bool
    event_is_test_drive: bool
    circuit: Optional[LinkRecord]
    car: Optional[LinkRecord]
    session: Optional[str]
