from collections.abc import Callable
from pathlib import Path


class LayerZeroMergeService:
    def __init__(self, *, merge_function: Callable[[Path], None]) -> None:
        self._merge_function = merge_function

    def merge(self, base_wiki_dir: Path) -> None:
        self._merge_function(base_wiki_dir)
