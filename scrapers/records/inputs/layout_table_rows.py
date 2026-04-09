from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LayoutTableRowsInput:
    """Input contract for layout table grouping mapper.

    Input: list of table rows with required `layout: str` field.
    Output: grouped list as {layout, lap_records} dictionaries.
    """

    rows: list[dict[str, Any]]



