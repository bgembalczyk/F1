from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SectionRecordInput:
    """Input contract for section -> record mapper.

    Required keys:
    - section_id: str
    - section_label: str
    - records: list[dict[str, Any]]
    - metadata: dict[str, Any]
    """

    payload: dict[str, Any]
