from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.seed.registry.entries import ListJobRegistryEntry


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
        return None


class MirrorConstructorsJobHook:
    def __init__(
        self,
        *,
        constructors_mirror_service: ConstructorsMirrorService,
        should_mirror_predicate: Callable[[ListJobRegistryEntry], bool],
    ) -> None:
        self._constructors_mirror_service = constructors_mirror_service
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
        self._constructors_mirror_service.mirror(base_wiki_dir, source_json_path)
