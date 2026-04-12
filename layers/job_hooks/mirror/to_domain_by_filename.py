import shutil
from collections.abc import Callable
from pathlib import Path

from layers.seed.registry.entries.list_job import ListJobRegistryEntry
from path_resolver.base import DEFAULT_PATH_RESOLVER


class MirrorToDomainByFilenameJobHook:
    def __init__(
        self,
        *,
        target_domain: str,
        should_mirror_predicate: Callable[[ListJobRegistryEntry], bool],
        allowed_filenames: tuple[str, ...] | None = None,
    ) -> None:
        self._target_domain = target_domain
        self._should_mirror_predicate = should_mirror_predicate
        self._allowed_filenames = allowed_filenames

    def after_job(
        self,
        *,
        base_wiki_dir: Path,
        job: ListJobRegistryEntry,
        l0_raw_json_path: Path,
    ) -> None:
        if not self._should_mirror_predicate(job):
            return

        source_json_path = base_wiki_dir / l0_raw_json_path
        if (
            self._allowed_filenames is not None
            and source_json_path.name not in self._allowed_filenames
        ):
            return

        target_rel_path = DEFAULT_PATH_RESOLVER.raw(
            domain=self._target_domain,
            filename=source_json_path.name,
        )
        target_path = base_wiki_dir / target_rel_path
        if target_path == source_json_path:
            return
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_json_path, target_path)
