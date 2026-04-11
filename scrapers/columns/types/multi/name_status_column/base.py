"""Base class for name+status columns that extract entity name with status markers.

This module provides a reusable abstraction for columns that parse entity names
(drivers, circuits, etc.) along with status information indicated by suffix markers.

Follows SOLID principles:
- Single Responsibility: Handles only name+status parsing
- Open/Closed: Extensible through configuration without modification
- DRY: Eliminates duplicate code across driver/circuit name columns
"""

from abc import ABC
from collections.abc import Callable

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.columns.types.function.base import FuncColumn
from scrapers.columns.types.mixins.background import BackgroundMixin
from scrapers.columns.types.mixins.enum import EnumMarksMixin
from scrapers.columns.types.multi.multi import MultiColumn
from scrapers.columns.types.url import UrlColumn


class NameStatusColumn(BackgroundMixin, MultiColumn, EnumMarksMixin, ABC):
    """
    Base class for columns that parse entity name with status markers.

    Common pattern:
    - Entity name with URL (e.g., "Lewis Hamilton", "Monaco")
    - Status indicated by suffix markers (e.g., "†", "*", "~")

    Inherits BackgroundMixin (adds background to record) and EnumMarksMixin
    (provides enum marks parsing helpers for subclasses).

    Subclasses define:
    - entity_key: The key for the entity name (e.g., "driver", "circuit")
    - status_extractors: Dict mapping status keys
      to extractor functions or BaseColumn instances
    """

    def __init__(
        self,
        entity_key: str,
        status_extractors: dict[str, BaseColumn | Callable[[ColumnContext], object]],
    ) -> None:
        """
        Initialize name+status column.

        Args:
            entity_key: Key for the entity name field
            status_extractors: Mapping of status field names to extractor functions
                or BaseColumn instances.
                Callables są automatycznie opakowane przez FuncColumn.
        """
        columns: dict[str, BaseColumn] = {entity_key: UrlColumn()}
        for status_key, extractor in status_extractors.items():
            if isinstance(extractor, BaseColumn):
                columns[status_key] = extractor
            else:
                columns[status_key] = FuncColumn(extractor)

        MultiColumn.__init__(self, columns)
        self.entity_key = entity_key
        self.status_extractors = status_extractors

    def enum_status_extractor(
        self,
        mapping: dict[str, object],
        *,
        default: object = None,
    ) -> Callable[[ColumnContext], object]:
        return lambda ctx: self.parse_marks(
            ctx,
            mapping=mapping,
            default=default,
        )


__all__ = [
    "NameStatusColumn",
]
