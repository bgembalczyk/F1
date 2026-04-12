from abc import ABC

from scrapers.parsers.constants_contracts import RecordT_co
from scrapers.parsers.constants_contracts import TableInputT_contra
from scrapers.parsers.parse_group_mixin import ParseGroupMixin


class GroupParsingMixin(ParseGroupMixin[TableInputT_contra, RecordT_co], ABC):
    """Backward-compatible alias for parse_group capability."""
