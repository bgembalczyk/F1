from __future__ import annotations

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
    from scrapers.circuits import complete_scraper  # noqa: F401
    from scrapers.circuits import circuits_list  # noqa: F401
    from scrapers.constructors import (  # noqa: F401
        constructors_2025_list,
        former_constructors_list,
        indianapolis_only_constructors_list,
        privateer_teams_list,
    )
    from scrapers.drivers import drivers_list  # noqa: F401
    from scrapers.engines import (  # noqa: F401
        engine_manufacturers_list,
        indianapolis_only_engine_manufacturers_list,
    )
    from scrapers.grands_prix import grands_prix_list  # noqa: F401
    from scrapers.seasons import seasons_list  # noqa: F401
