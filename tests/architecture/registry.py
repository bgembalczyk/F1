from __future__ import annotations

from dataclasses import dataclass

from scripts.ci.architecture_spec import ARCHITECTURE_SPEC


@dataclass(frozen=True)
class ArchitectureRegistry:
    domain_names: tuple[str, ...]
    entrypoint_domains: tuple[str, ...]
    layers: tuple[str, ...]
    forbidden_imports_by_layer: dict[str, tuple[str, ...]]
    required_layers_by_domain: dict[str, tuple[str, ...]]
    allowed_imports_by_layer: dict[str, tuple[str, ...]]
    entrypoint_modules: tuple[str, ...]
    entrypoint_files: tuple[str, ...]


ARCHITECTURE_REGISTRY = ArchitectureRegistry(
    domain_names=ARCHITECTURE_SPEC.domain_names,
    entrypoint_domains=ARCHITECTURE_SPEC.entrypoint_domains,
    layers=ARCHITECTURE_SPEC.layers,
    forbidden_imports_by_layer=ARCHITECTURE_SPEC.forbidden_imports_by_layer,
    required_layers_by_domain=ARCHITECTURE_SPEC.required_layers_by_domain,
    allowed_imports_by_layer=ARCHITECTURE_SPEC.allowed_imports_by_layer,
    entrypoint_modules=ARCHITECTURE_SPEC.entrypoint_modules,
    entrypoint_files=ARCHITECTURE_SPEC.entrypoint_files,
)
