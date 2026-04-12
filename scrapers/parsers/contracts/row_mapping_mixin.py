from abc import ABC
from abc import abstractmethod
from typing import Generic

from scrapers.parsers.contracts.constants_mapping_contracts import RecordT_co
from scrapers.parsers.contracts.constants_mapping_contracts import RowInputT_contra


class RowMappingMixin(ABC, Generic[RowInputT_contra, RecordT_co]):
    @abstractmethod
    def map_row(self, row: RowInputT_contra) -> RecordT_co | None: ...
