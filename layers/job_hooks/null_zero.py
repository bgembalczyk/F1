from pathlib import Path

from layers.seed.registry.entries.list_job import ListJobRegistryEntry


class NullLayerZeroJobHook:
    def after_job(
        self,
        *,
        base_wiki_dir: Path,
        job: ListJobRegistryEntry,
        l0_raw_json_path: Path,
    ) -> None:
        _ = (base_wiki_dir, job, l0_raw_json_path)


