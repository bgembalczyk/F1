from abc import ABC
from abc import abstractmethod
from typing import Generic

from scrapers.parsers.contracts.constants_mapping_contracts import RecordT_co
from scrapers.parsers.contracts.constants_mapping_contracts import TableInputT_contra


class ParseGroupMixin(ABC, Generic[TableInputT_contra, RecordT_co]):
    @abstractmethod
    def parse_group(self, table: TableInputT_contra) -> list[RecordT_co]: ...
