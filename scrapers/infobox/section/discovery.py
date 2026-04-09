from typing import Protocol


class InfoboxSectionDiscovery(Protocol):
    def collect(self, table: object) -> list[dict[str, object]]: ...
