"""Shared abstractions and registry for domain list-scraper entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.base.domain_registry import get_domain_registry_entry
from scrapers.base.domain_registry import get_domain_entrypoint_scraper_metadata
from scrapers.base.domain_registry import import_target
from scrapers.base.domain_registry import render_registry_output_path
from scrapers.base.domain_registry import run_config_profile_for
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


class LazyScraperClassProxy:
    """Lazy wrapper that resolves a scraper class only when it is actually used."""

    def __init__(self, import_path: str) -> None:
        self._import_path = import_path
        self._resolved_cls: type[ABCScraper] | None = None

    def _resolve(self) -> type[ABCScraper]:
        if self._resolved_cls is None:
            self._resolved_cls = import_target(self._import_path)
        return self._resolved_cls

    def __call__(self, *args: object, **kwargs: object) -> object:
        return self._resolve()(*args, **kwargs)

    def __getattr__(self, name: str) -> object:
        return getattr(self._resolve(), name)

    def __repr__(self) -> str:
        return f"LazyScraperClassProxy({self._import_path!r})"



@cache
def _resolve_domain_entrypoint_config(domain: str) -> DomainEntrypointConfig:
    entry = get_domain_registry_entry(domain)
    return DomainEntrypointConfig(
        list_scraper_cls=LazyScraperClassProxy(entry.scraper_path),
        default_output_json=render_registry_output_path(
            domain=domain,
            path=entry.default_output_json,
        ),
        default_output_csv=render_registry_output_path(
            domain=domain,
            path=entry.default_output_csv,
        ),
        run_config_profile=run_config_profile_for(entry.run_profile_name),
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
