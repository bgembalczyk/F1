from abc import ABC

from scrapers.parsers.contracts.constants_contracts import RecordT_co
from scrapers.parsers.contracts.constants_contracts import TableInputT_contra
from scrapers.parsers.contracts.parse_group_mixin import ParseGroupMixin


class GroupParsingMixin(ParseGroupMixin[TableInputT_contra, RecordT_co], ABC):
    """Backward-compatible alias for parse_group capability."""
