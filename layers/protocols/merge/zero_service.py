from pathlib import Path
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class LayerZeroMergeServiceProtocol(Protocol):
    def merge(self, base_wiki_dir: Path) -> None: ...
