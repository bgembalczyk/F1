from pathlib import Path
from typing import Protocol
from typing import runtime_checkable

from scrapers.run_config import RunConfig


@runtime_checkable
class LayerExecutorProtocol(Protocol):
    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None: ...
