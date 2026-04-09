from typing import Protocol
from typing import runtime_checkable

from pathlib import Path


@runtime_checkable
class LayerZeroMergeServiceProtocol(Protocol):
    def merge(self, base_wiki_dir: Path) -> None: ...
