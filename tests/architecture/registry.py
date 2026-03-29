from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DomainArchitecture:
    name: str
    has_entrypoint: bool
    required_layers: tuple[str, ...]


@dataclass(frozen=True)
class ArchitectureRegistry:
    domains: tuple[DomainArchitecture, ...]
    layers: tuple[str, ...]
    forbidden_imports_by_layer: dict[str, tuple[str, ...]]
    architecture_sensitive_paths: tuple[str, ...]

    @property
    def domain_names(self) -> tuple[str, ...]:
        return tuple(domain.name for domain in self.domains)

    @property
    def entrypoint_domains(self) -> tuple[str, ...]:
        return tuple(domain.name for domain in self.domains if domain.has_entrypoint)

    @property
    def required_layers_by_domain(self) -> dict[str, tuple[str, ...]]:
        return {domain.name: domain.required_layers for domain in self.domains if domain.has_entrypoint}

    @property
    def allowed_imports_by_layer(self) -> dict[str, tuple[str, ...]]:
        return {
            layer: tuple(
                sorted(
                    set(self.layers) - {layer} - set(self.forbidden_imports_by_layer[layer]),
                ),
            )
            for layer in self.layers
        }

    @property
    def entrypoint_modules(self) -> tuple[str, ...]:
        return tuple(f"scrapers.{domain}.entrypoint" for domain in self.entrypoint_domains)

    @property
    def entrypoint_files(self) -> tuple[str, ...]:
        return tuple(f"scrapers/{domain}/entrypoint.py" for domain in self.entrypoint_domains)


ARCHITECTURE_REGISTRY = ArchitectureRegistry(
    domains=(
        DomainArchitecture("drivers", True, ("list", "sections", "infobox", "postprocess")),
        DomainArchitecture("constructors", True, ("list", "sections", "infobox", "postprocess")),
        DomainArchitecture("circuits", True, ("list", "sections", "infobox", "postprocess")),
        DomainArchitecture("seasons", True, ("list", "sections", "postprocess")),
        DomainArchitecture("grands_prix", True, ("list", "sections")),
        DomainArchitecture("engines", False, ()),
        DomainArchitecture("points", False, ()),
        DomainArchitecture("sponsorship_liveries", False, ()),
        DomainArchitecture("tyres", False, ()),
    ),
    layers=("list", "sections", "infobox", "postprocess"),
    forbidden_imports_by_layer={
        "list": ("infobox", "postprocess"),
        "sections": ("list", "single_scraper"),
        "infobox": ("list", "sections", "postprocess", "single_scraper"),
        "postprocess": ("list", "sections", "infobox", "single_scraper"),
    },
    architecture_sensitive_paths=(
        "layers/",
        "scrapers/base/",
        "tests/architecture/",
    ),
)
