from __future__ import annotations

from collections.abc import Callable
import shutil
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Protocol

from layers.path_resolver import DEFAULT_PATH_RESOLVER

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from layers.constructors_mirror_service import ConstructorsMirrorService
    from layers.seed.registry import ListJobRegistryEntry


class LayerZeroJobHook(Protocol):
    def after_job(
        self,
        *,
        base_wiki_dir: Path,
        job: ListJobRegistryEntry,
        l0_raw_json_path: Path,
    ) -> None: ...


class NullLayerZeroJobHook:
    def after_job(
        self,
        *,
        base_wiki_dir: Path,
        job: ListJobRegistryEntry,
        l0_raw_json_path: Path,
    ) -> None:
        _ = (base_wiki_dir, job, l0_raw_json_path)


class CompositeLayerZeroJobHook:
    def __init__(self, *, hooks: tuple[LayerZeroJobHook, ...]) -> None:
        self._hooks = hooks

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


class MirrorConstructorsJobHook:
    def __init__(
        self,
        *,
        mirror: ConstructorsMirrorService | None = None,
        constructors_mirror_service: ConstructorsMirrorService | None = None,
        should_mirror_predicate: Callable[[ListJobRegistryEntry], bool],
    ) -> None:
        self._mirror = mirror or constructors_mirror_service
        if self._mirror is None:
            msg = "MirrorConstructorsJobHook requires `mirror` service."
            raise ValueError(msg)
        self._should_mirror_predicate = should_mirror_predicate

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
        self._mirror.mirror(base_wiki_dir, source_json_path)


class MirrorToDomainByFilenameJobHook:
    def __init__(
        self,
        *,
        target_domain: str,
        should_mirror_predicate: Callable[[ListJobRegistryEntry], bool],
    ) -> None:
        self._target_domain = target_domain
        self._should_mirror_predicate = should_mirror_predicate

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
        target_rel_path = DEFAULT_PATH_RESOLVER.raw(
            domain=self._target_domain,
            filename=source_json_path.name,
        )
        target_path = base_wiki_dir / target_rel_path
        if target_path == source_json_path:
            return
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_json_path, target_path)
