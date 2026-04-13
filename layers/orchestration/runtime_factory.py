from __future__ import annotations

import importlib
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RuntimeComponentKey:
    role: str
    domain: str
    stage: str

    @classmethod
    def build(cls, *, role: str, domain: str, stage: str) -> RuntimeComponentKey:
        return cls(
            role=role.strip(),
            domain=domain.strip(),
            stage=stage.strip(),
        )


class RuntimeComponentFactory:
    def __init__(self) -> None:
        self._builders: dict[RuntimeComponentKey, Callable[[], object]] = {}
        self._source_by_key: dict[RuntimeComponentKey, str] = {}

    def register(
        self,
        *,
        role: str,
        domain: str,
        stage: str,
        builder: Callable[[], object],
        source: str,
    ) -> None:
        key = RuntimeComponentKey.build(role=role, domain=domain, stage=stage)
        self._validate_key(key)
        self._validate_source(source)
        self._validate_duplicate_registration(key=key, source=source)
        self._builders[key] = builder
        self._source_by_key[key] = source

    def register_instance(
        self,
        *,
        role: str,
        domain: str,
        stage: str,
        instance: object,
        source: str,
    ) -> None:
        self.register(
            role=role,
            domain=domain,
            stage=stage,
            builder=lambda: instance,
            source=source,
        )

    def build(self, *, role: str, domain: str, stage: str) -> object:
        key = RuntimeComponentKey.build(role=role, domain=domain, stage=stage)
        builder = self._builders.get(key)
        if builder is None:
            msg = (
                "Component is not registered in runtime factory for "
                f"role={role!r}, domain={domain!r}, stage={stage!r}"
            )
            raise KeyError(msg)
        return builder()

    def discover_and_register(
        self,
        *,
        root: Path,
        module_globs: tuple[str, ...],
    ) -> None:
        for module_name in self._iter_module_names(
            root=root,
            module_globs=module_globs,
        ):
            module = importlib.import_module(module_name)
            self._register_from_module(module)

    @staticmethod
    def _iter_module_names(
        *,
        root: Path,
        module_globs: tuple[str, ...],
    ) -> tuple[str, ...]:
        module_paths: set[Path] = set()
        for module_glob in module_globs:
            module_paths.update(root.glob(module_glob))
        names = []
        for path in module_paths:
            if not path.is_file():
                continue
            rel = path.relative_to(root).with_suffix("")
            names.append(".".join(rel.parts))
        return tuple(sorted(names))

    def _register_from_module(self, module: Any) -> None:
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if candidate.__module__ != module.__name__:
                continue
            role = getattr(candidate, "role", None)
            domain = getattr(candidate, "domain", None)
            stage = getattr(candidate, "stage", None)
            if not all(isinstance(value, str) for value in (role, domain, stage)):
                continue
            self.register(
                role=role,
                domain=domain,
                stage=stage,
                builder=candidate,
                source=f"{candidate.__module__}.{candidate.__qualname__}",
            )

    @staticmethod
    def _validate_key(key: RuntimeComponentKey) -> None:
        if not key.role or not key.domain or not key.stage:
            msg = (
                "Runtime component key requires non-empty role/domain/stage, "
                f"got {key}"
            )
            raise ValueError(msg)

    @staticmethod
    def _validate_source(source: str) -> None:
        if not source.strip():
            msg = "Runtime component source cannot be empty"
            raise ValueError(msg)

    def _validate_duplicate_registration(
        self,
        *,
        key: RuntimeComponentKey,
        source: str,
    ) -> None:
        existing_source = self._source_by_key.get(key)
        if existing_source is None:
            return
        if existing_source == source:
            msg = (
                "Duplicate runtime registration detected for "
                f"key={key} source={source!r}"
            )
            raise ValueError(msg)
        msg = (
            "Runtime key conflict detected for "
            f"key={key}: existing={existing_source!r} new={source!r}"
        )
        raise ValueError(msg)
