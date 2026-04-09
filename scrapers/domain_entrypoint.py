"""Shared abstractions and registry for domain list-scraper entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from functools import cache
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Protocol

from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile
from scrapers.base.runner import ScraperRunner

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


class OutputPathRenderer(Protocol):
    """Policy contract for rendering configured output paths per domain."""

    def render(self, path: str | Path | None) -> str | Path | None: ...


@dataclass(frozen=True)
class IdentityOutputPathRenderer:
    """No-op renderer for domains without placeholders in output paths."""

    def render(self, path: str | Path | None) -> str | Path | None:
        return path


@dataclass(frozen=True)
class YearPlaceholderOutputPathRenderer:
    """Renderer replacing ``{year}`` placeholder with the configured year value."""

    year: int | None

    def render(self, path: str | Path | None) -> str | Path | None:
        if path is None or self.year is None:
            return path
        if isinstance(path, Path):
            return Path(str(path).format(year=self.year))
        return path.format(year=self.year)


@dataclass(frozen=True)
class CurrentYearOutputPathRenderer:
    """Renderer that resolves ``CURRENT_YEAR`` lazily from a module attribute."""

    module_path: str
    attr_name: str = "CURRENT_YEAR"

    def render(self, path: str | Path | None) -> str | Path | None:
        year = getattr(import_module(self.module_path), self.attr_name, None)
        return YearPlaceholderOutputPathRenderer(year=year).render(path)


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


@dataclass(frozen=True)
class _DomainEntrypointSpec:
    scraper_path: str
    default_output_json: str | Path
    run_config_profile: Callable[[], RunConfig]
    default_output_csv: str | Path | None = None
    output_path_renderer: OutputPathRenderer = field(
        default_factory=IdentityOutputPathRenderer,
    )


def default_profile() -> RunConfig:
    """Default production-oriented profile."""
    return build_run_profile(RunProfileName.DEFAULT)


def debug_profile() -> RunConfig:
    """Profile with debug dumps enabled."""
    return build_run_profile(RunProfileName.DEBUG)


_DOMAIN_ENTRYPOINT_SPECS: dict[str, _DomainEntrypointSpec] = {
    "drivers": _DomainEntrypointSpec(
        scraper_path="scrapers.drivers.list_scraper:F1DriversListScraper",
        default_output_json="drivers/f1_drivers.json",
        run_config_profile=default_profile,
    ),
    "seasons": _DomainEntrypointSpec(
        scraper_path="scrapers.seasons.list_scraper:SeasonsListScraper",
        default_output_json="seasons/f1_seasons.json",
        default_output_csv="seasons/f1_seasons.csv",
        run_config_profile=default_profile,
    ),
    "grands_prix": _DomainEntrypointSpec(
        scraper_path="scrapers.grands_prix.list_scraper:GrandsPrixListScraper",
        default_output_json="grands_prix/f1_grands_prix_by_title.json",
        default_output_csv="grands_prix/f1_grands_prix_by_title.csv",
        run_config_profile=default_profile,
    ),
    "circuits": _DomainEntrypointSpec(
        scraper_path="scrapers.circuits.list_scraper:CircuitsListScraper",
        default_output_json="circuits/f1_circuits.json",
        default_output_csv="circuits/f1_circuits.csv",
        run_config_profile=default_profile,
    ),
    "constructors": _DomainEntrypointSpec(
        scraper_path=(
            "scrapers.constructors.current_constructors_list:"
            "CurrentConstructorsListScraper"
        ),
        default_output_json="constructors/f1_constructors_{year}.json",
        default_output_csv="constructors/f1_constructors_{year}.csv",
        run_config_profile=debug_profile,
        output_path_renderer=CurrentYearOutputPathRenderer(
            module_path="scrapers.constructors.constants",
        ),
    ),
}


def get_domain_entrypoint_scraper_metadata() -> dict[str, str]:
    """Return static domain-to-scraper-path metadata for command generation."""
    return {
        domain: spec.scraper_path for domain, spec in _DOMAIN_ENTRYPOINT_SPECS.items()
    }


def _import_target(path: str) -> object:
    module_name, attr_name = path.split(":", maxsplit=1)
    module = import_module(module_name)
    return getattr(module, attr_name)


@cache
def _resolve_domain_entrypoint_config(domain: str) -> DomainEntrypointConfig:
    spec = _DOMAIN_ENTRYPOINT_SPECS[domain]
    list_scraper_cls = LazyScraperClassProxy(spec.scraper_path)

    return DomainEntrypointConfig(
        list_scraper_cls=list_scraper_cls,
        default_output_json=spec.output_path_renderer.render(spec.default_output_json),
        default_output_csv=spec.output_path_renderer.render(spec.default_output_csv),
        run_config_profile=spec.run_config_profile,
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


def install_domain_entrypoint(
    module_globals: dict[str, object],
    *,
    domain: str,
) -> None:
    """Install standard domain-entrypoint shims into ``module_globals``."""
    module_globals["run_list_scraper"] = build_run_list_scraper_for_domain(domain)
    module_globals["__getattr__"] = build_entrypoint_alias_getattr_for_domain(domain)
