"""Shared abstractions and registry for domain list-scraper entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile

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



@dataclass(frozen=True)
class _DomainEntrypointSpec:
    scraper_path: str
    default_output_json: str | Path
    run_config_profile: Callable[[], RunConfig]
    default_output_csv: str | Path | None = None


def strict_quality_profile() -> RunConfig:
    """Profile with stricter diagnostics enabled."""
    return build_run_profile(RunProfileName.STRICT)


def minimal_profile() -> RunConfig:
    """Profile with a minimal production-oriented configuration."""
    return build_run_profile(RunProfileName.MINIMAL)


def minimal_debug_profile() -> RunConfig:
    """Profile with minimal checks and debug dumps enabled."""
    return build_run_profile(RunProfileName.DEBUG)


_DOMAIN_ENTRYPOINT_SPECS: dict[str, _DomainEntrypointSpec] = {
    "drivers": _DomainEntrypointSpec(
        scraper_path="scrapers.drivers.list_scraper:F1DriversListScraper",
        default_output_json="drivers/f1_drivers.json",
        run_config_profile=strict_quality_profile,
    ),
    "seasons": _DomainEntrypointSpec(
        scraper_path="scrapers.seasons.list_scraper:SeasonsListScraper",
        default_output_json="seasons/f1_seasons.json",
        default_output_csv="seasons/f1_seasons.csv",
        run_config_profile=minimal_profile,
    ),
    "grands_prix": _DomainEntrypointSpec(
        scraper_path="scrapers.grands_prix.list_scraper:GrandsPrixListScraper",
        default_output_json="grands_prix/f1_grands_prix_by_title.json",
        default_output_csv="grands_prix/f1_grands_prix_by_title.csv",
        run_config_profile=minimal_profile,
    ),
    "circuits": _DomainEntrypointSpec(
        scraper_path="scrapers.circuits.list_scraper:CircuitsListScraper",
        default_output_json="circuits/f1_circuits.json",
        default_output_csv="circuits/f1_circuits.csv",
        run_config_profile=strict_quality_profile,
    ),
    "constructors": _DomainEntrypointSpec(
        scraper_path=(
            "scrapers.constructors.current_constructors_list:"
            "CurrentConstructorsListScraper"
        ),
        default_output_json="constructors/f1_constructors_{year}.json",
        default_output_csv="constructors/f1_constructors_{year}.csv",
        run_config_profile=minimal_debug_profile,
    ),
}


def _import_target(path: str) -> object:
    module_name, attr_name = path.split(":", maxsplit=1)
    module = import_module(module_name)
    return getattr(module, attr_name)


@cache
def _resolve_domain_entrypoint_config(domain: str) -> DomainEntrypointConfig:
    spec = _DOMAIN_ENTRYPOINT_SPECS[domain]
    list_scraper_cls = LazyScraperClassProxy(spec.scraper_path)
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

    return DomainEntrypointConfig(
        list_scraper_cls=list_scraper_cls,
        default_output_json=_render(spec.default_output_json),
        default_output_csv=_render(spec.default_output_csv),
        run_config_profile=spec.run_config_profile,
    )


def get_domain_entrypoint_config(domain: str) -> DomainEntrypointConfig:
    """Return standardized list-scraper entrypoint configuration for a domain."""
    return _resolve_domain_entrypoint_config(domain)


def build_run_list_scraper(
    *,
    list_scraper_cls: type[ABCScraper],
    default_output_json: str | Path,
    default_profile: Callable[[], RunConfig],
    default_output_csv: str | Path | None = None,
) -> Callable[..., None]:
    """Build a standardized ``run_list_scraper`` facade for domain entrypoints."""

    return build_run_list_scraper_from_config(
        DomainEntrypointConfig(
            list_scraper_cls=list_scraper_cls,
            default_output_json=default_output_json,
            default_output_csv=default_output_csv,
            run_config_profile=default_profile,
        ),
    )


def build_run_list_scraper_from_config(
    config: DomainEntrypointConfig,
) -> Callable[..., None]:
    """Build a standardized ``run_list_scraper`` facade from declarative config."""

    def run_list_scraper(*, run_config: RunConfig | None = None) -> None:
        resolved_config = run_config or config.run_config_profile()
        run_and_export(
            config.list_scraper_cls,
            config.default_output_json,
            config.default_output_csv,
            run_config=resolved_config,
        )

    return run_list_scraper


def build_run_list_scraper_for_domain(domain: str) -> Callable[..., None]:
    """Build ``run_list_scraper`` facade that resolves its config lazily by domain."""

    def run_list_scraper(*, run_config: RunConfig | None = None) -> None:
        config = get_domain_entrypoint_config(domain)
        resolved_config = run_config or config.run_config_profile()
        run_and_export(
            config.list_scraper_cls,
            config.default_output_json,
            config.default_output_csv,
            run_config=resolved_config,
        )

    return run_list_scraper
