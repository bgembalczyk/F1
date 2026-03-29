"""Shared abstractions and registry for domain list-scraper entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile
from scrapers.base.runner import ScraperRunner
from tests.architecture.rules import ArchitectureDomainSpec
from tests.architecture.rules import get_entrypoint_domain_specs
from tests.architecture.rules import validate_architecture_registry_or_raise

if TYPE_CHECKING:
    from collections.abc import Callable

    from scrapers.base.abc import ABCScraper
    from scrapers.base.run_config import RunConfig


@dataclass(frozen=True)
class DomainEntrypointConfig:
    """Declarative configuration for a domain ``run_list_scraper`` facade."""

    list_scraper_cls: type[ABCScraper] | LazyScraperClassProxy
    default_output_json: str | Path
    run_config_profile: Callable[[], RunConfig]
    default_output_csv: str | Path | None = None


class LazyScraperClassProxy:
    """Lazy wrapper that resolves a scraper class only when it is actually used."""

    def __init__(self, import_path: str) -> None:
        self._import_path = import_path
        self._resolved_cls: type[ABCScraper] | None = None

    def _resolve(self) -> type[ABCScraper]:
        if self._resolved_cls is None:
            self._resolved_cls = _import_target(self._import_path)
        return self._resolved_cls

    def __call__(self, *args: object, **kwargs: object) -> object:
        return self._resolve()(*args, **kwargs)

    def __getattr__(self, name: str) -> object:
        return getattr(self._resolve(), name)

    def __repr__(self) -> str:
        return f"LazyScraperClassProxy({self._import_path!r})"


def strict_quality_profile() -> RunConfig:
    """Profile with stricter diagnostics enabled."""
    return build_run_profile(RunProfileName.STRICT)


def minimal_profile() -> RunConfig:
    """Profile with a minimal production-oriented configuration."""
    return build_run_profile(RunProfileName.MINIMAL)


def minimal_debug_profile() -> RunConfig:
    """Profile with minimal checks and debug dumps enabled."""
    return build_run_profile(RunProfileName.DEBUG)


_PROFILE_BUILDERS: dict[str, Callable[[], RunConfig]] = {
    "strict_quality": strict_quality_profile,
    "minimal": minimal_profile,
    "minimal_debug": minimal_debug_profile,
}


def _load_entrypoint_specs() -> dict[str, ArchitectureDomainSpec]:
    validate_architecture_registry_or_raise()
    return {spec.domain: spec for spec in get_entrypoint_domain_specs()}


_DOMAIN_ENTRYPOINT_SPECS: dict[str, ArchitectureDomainSpec] = _load_entrypoint_specs()


def get_domain_entrypoint_scraper_metadata() -> dict[str, str]:
    """Return static domain-to-scraper-path metadata for command generation."""
    return {
        domain: spec.entrypoint_scraper_path
        for domain, spec in _DOMAIN_ENTRYPOINT_SPECS.items()
        if spec.entrypoint_scraper_path is not None
    }


def _import_target(path: str) -> object:
    module_name, attr_name = path.split(":", maxsplit=1)
    module = import_module(module_name)
    return getattr(module, attr_name)


@cache
def _resolve_domain_entrypoint_config(domain: str) -> DomainEntrypointConfig:
    spec = _DOMAIN_ENTRYPOINT_SPECS[domain]
    scraper_path = spec.entrypoint_scraper_path
    if scraper_path is None:
        raise KeyError(domain)
    list_scraper_cls = LazyScraperClassProxy(scraper_path)

    current_year = None
    if domain == "constructors":
        current_year = getattr(
            import_module("scrapers.constructors.constants"),
            "CURRENT_YEAR",
            None,
        )

    def _render(path: str | Path | None) -> str | Path | None:
        if path is None or current_year is None:
            return path
        if isinstance(path, Path):
            return Path(str(path).format(year=current_year))
        return path.format(year=current_year)

    run_profile_name = spec.entrypoint_run_profile
    if run_profile_name is None:
        raise KeyError(domain)

    return DomainEntrypointConfig(
        list_scraper_cls=list_scraper_cls,
        default_output_json=_render(spec.entrypoint_output_json),
        default_output_csv=_render(spec.entrypoint_output_csv),
        run_config_profile=_PROFILE_BUILDERS[run_profile_name],
    )


def get_domain_entrypoint_config(domain: str) -> DomainEntrypointConfig:
    """Return standardized list-scraper entrypoint configuration for a domain."""
    return _resolve_domain_entrypoint_config(domain)


def build_entrypoint_alias_getattr_for_domain(domain: str) -> Callable[[str], object]:
    """Build ``__getattr__`` that exposes standardized domain entrypoint aliases."""

    def _module_getattr(name: str) -> object:
        config = get_domain_entrypoint_config(domain)
        aliases: dict[str, object] = {
            "ENTRYPOINT_CONFIG": config,
            "LIST_SCRAPER_CLASS": config.list_scraper_cls,
            "DEFAULT_OUTPUT_JSON": config.default_output_json,
            "RUN_CONFIG_PROFILE": config.run_config_profile,
        }
        if config.default_output_csv is not None:
            aliases["DEFAULT_OUTPUT_CSV"] = config.default_output_csv

        if name not in aliases:
            msg = f"module {__name__!r} has no attribute {name!r}"
            raise AttributeError(msg)
        return aliases[name]

    return _module_getattr


def build_run_list_scraper_for_domain(domain: str) -> Callable[..., None]:
    """Build ``run_list_scraper`` facade that resolves its config lazily by domain."""

    def run_list_scraper(*, run_config: RunConfig | None = None) -> None:
        config = get_domain_entrypoint_config(domain)
        resolved_config = run_config or config.run_config_profile()
        ScraperRunner(resolved_config).run_and_export(
            config.list_scraper_cls,
            config.default_output_json,
            config.default_output_csv,
        )

    return run_list_scraper
