from typing import Protocol

from pathlib import Path

from layers.seed.registry.entries.list_job import ListJobRegistryEntry


class LayerZeroJobHook(Protocol):
    def after_job(
        self,
        *,
        base_wiki_dir: Path,
        job: ListJobRegistryEntry,
        l0_raw_json_path: Path,
    ) -> None: ...
