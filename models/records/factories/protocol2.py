from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

from models.records.factories.build import RECORD_BUILDERS
from models.records.factories.build import RecordType

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping


class RecordFactory(Protocol):
    """Unified contract for record creation used by scraper configuration."""

    def create(self, payload: Mapping[str, Any]) -> Any: ...


