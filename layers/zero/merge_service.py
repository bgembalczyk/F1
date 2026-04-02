from collections.abc import Callable
from pathlib import Path


class LayerZeroMergeService:
    def __init__(
        self,
        *,
        merge: Callable[[Path], None] | None = None,
        merge_function: Callable[[Path], None] | None = None,
    ) -> None:
        self._merge = merge or merge_function
        if self._merge is None:
            msg = "LayerZeroMergeService requires `merge` callable."
            raise ValueError(msg)

    def merge(self, base_wiki_dir: Path) -> None:
        self._merge(base_wiki_dir)
