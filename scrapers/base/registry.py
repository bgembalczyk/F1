from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional, Type

from scrapers.base.scraper import F1Scraper
from scrapers.config import ScraperConfig, default_config


@dataclass(frozen=True)
class ScraperRegistryConfig:
    name: str
    scraper_cls: Type[F1Scraper]
    json_rel: Path
    csv_rel: Optional[Path]
    config_factory: Callable[[], ScraperConfig] = default_config


SCRAPER_REGISTRY: Dict[str, ScraperRegistryConfig] = {}


def register_scraper(
    name: str,
    json_rel: str | Path,
    csv_rel: str | Path | None,
    *,
    config_factory: Callable[[], ScraperConfig] = default_config,
):
    def decorator(scraper_cls: Type[F1Scraper]) -> Type[F1Scraper]:
        if name in SCRAPER_REGISTRY:
            raise ValueError(f"Scraper '{name}' jest już zarejestrowany.")

        SCRAPER_REGISTRY[name] = ScraperRegistryConfig(
            name=name,
            scraper_cls=scraper_cls,
            json_rel=Path(json_rel),
            csv_rel=Path(csv_rel) if csv_rel is not None else None,
            config_factory=config_factory,
        )
        return scraper_cls

    return decorator


def load_default_scrapers() -> None:
    import scrapers

    for module_info in pkgutil.walk_packages(scrapers.__path__, prefix="scrapers."):
        if module_info.ispkg:
            continue

        if module_info.name.startswith("scrapers.base."):
            continue

        if module_info.name == "scrapers.config":
            continue

        importlib.import_module(module_info.name)
