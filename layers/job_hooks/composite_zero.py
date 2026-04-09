from pathlib import Path

from layers.protocols.zero_job_hook import LayerZeroJobHook
from layers.seed.registry.entries.list_job import ListJobRegistryEntry


class CompositeLayerZeroJobHook:
    def __init__(self, *, hooks: tuple[LayerZeroJobHook, ...]) -> None:
        self._hooks = hooks

    @property
    def hooks(self) -> tuple[LayerZeroJobHook, ...]:
        return self._hooks

    def after_job(
        self,
        *,
        base_wiki_dir: Path,
        job: ListJobRegistryEntry,
        l0_raw_json_path: Path,
    ) -> None:
        for hook in self._hooks:
            hook.after_job(
                base_wiki_dir=base_wiki_dir,
                job=job,
                l0_raw_json_path=l0_raw_json_path,
            )
