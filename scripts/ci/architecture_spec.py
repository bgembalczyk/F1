from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DomainSpec:
    name: str
    has_entrypoint: bool
    required_layers: tuple[str, ...]


@dataclass(frozen=True)
class LegacyLifecycle:
    stage: str
    description: str


@dataclass(frozen=True)
class LegacyModuleMapping:
    old_module: str
    new_module: str
    notes: str = ""


@dataclass(frozen=True)
class ArchitectureSpec:
    domains: tuple[DomainSpec, ...]
    layers: tuple[str, ...]
    forbidden_imports_by_layer: dict[str, tuple[str, ...]]
    legacy_lifecycle: tuple[LegacyLifecycle, ...]
    legacy_module_mappings: tuple[LegacyModuleMapping, ...]

    @property
    def domain_names(self) -> tuple[str, ...]:
        return tuple(domain.name for domain in self.domains)

    @property
    def entrypoint_domains(self) -> tuple[str, ...]:
        return tuple(domain.name for domain in self.domains if domain.has_entrypoint)

    @property
    def required_layers_by_domain(self) -> dict[str, tuple[str, ...]]:
        return {
            domain.name: domain.required_layers
            for domain in self.domains
            if domain.has_entrypoint
        }

    @property
    def allowed_imports_by_layer(self) -> dict[str, tuple[str, ...]]:
        return {
            layer: tuple(
                sorted(
                    set(self.layers)
                    - {layer}
                    - set(self.forbidden_imports_by_layer[layer]),
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


ARCHITECTURE_SPEC = ArchitectureSpec(
    domains=(
        DomainSpec("drivers", True, ("list", "sections", "infobox", "postprocess")),
        DomainSpec("constructors", True, ("list", "sections", "infobox", "postprocess")),
        DomainSpec("circuits", True, ("list", "sections", "infobox", "postprocess")),
        DomainSpec("seasons", True, ("list", "sections", "postprocess")),
        DomainSpec("grands_prix", True, ("list", "sections")),
        DomainSpec("engines", False, ()),
        DomainSpec("points", False, ()),
        DomainSpec("sponsorship_liveries", False, ()),
        DomainSpec("tyres", False, ()),
    ),
    layers=("list", "sections", "infobox", "postprocess"),
    forbidden_imports_by_layer={
        "list": ("infobox", "postprocess"),
        "sections": ("list", "single_scraper"),
        "infobox": ("list", "sections", "postprocess", "single_scraper"),
        "postprocess": ("list", "sections", "infobox", "single_scraper"),
    },
    legacy_lifecycle=(
        LegacyLifecycle("R0", "legacy działa + obowiązkowy DeprecationWarning"),
        LegacyLifecycle("R1", "legacy nadal działa + warning pozostaje obowiązkowy"),
        LegacyLifecycle("R2", "legacy entrypointy usuwane"),
    ),
    legacy_module_mappings=(
        LegacyModuleMapping("scrapers.circuits.list_scraper", "scrapers.circuits.entrypoint"),
        LegacyModuleMapping(
            "scrapers.constructors.current_constructors_list",
            "scrapers.constructors.entrypoint",
        ),
        LegacyModuleMapping("scrapers.drivers.list_scraper", "scrapers.drivers.entrypoint"),
        LegacyModuleMapping(
            "scrapers.grands_prix.list_scraper",
            "scrapers.grands_prix.entrypoint",
        ),
        LegacyModuleMapping("scrapers.seasons.list_scraper", "scrapers.seasons.entrypoint"),
        LegacyModuleMapping(
            "python main.py --mode <layer0|layer1|full>",
            "python -m scrapers.cli wiki --mode <layer0|layer1|full>",
            notes="canonical launcher",
        ),
    ),
)
