from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Type

from scrapers.base.scraper import F1Scraper


@dataclass(frozen=True)
class ScraperConfig:
    name: str
    scraper_cls: Type[F1Scraper]
    json_rel: Path
    csv_rel: Optional[Path]
    default_kwargs: Dict[str, Any] = field(default_factory=dict)


SCRAPER_REGISTRY: Dict[str, ScraperConfig] = {}


def register_scraper(
    name: str,
    json_rel: str | Path,
    csv_rel: str | Path | None,
    **default_kwargs: Any,
):
    def decorator(scraper_cls: Type[F1Scraper]) -> Type[F1Scraper]:
        if name in SCRAPER_REGISTRY:
            raise ValueError(f"Scraper '{name}' jest już zarejestrowany.")

        SCRAPER_REGISTRY[name] = ScraperConfig(
            name=name,
            scraper_cls=scraper_cls,
            json_rel=Path(json_rel),
            csv_rel=Path(csv_rel) if csv_rel is not None else None,
            default_kwargs=dict(default_kwargs),
        )
        return scraper_cls

    return decorator


def load_default_scrapers() -> None:
    from scrapers.circuits import complete_scraper  # noqa: F401
    from scrapers.circuits import list_scraper  # noqa: F401
    from scrapers.constructors import (  # noqa: F401
        F1_constructors_2025_list_scraper,
        F1_former_constructors_list_scraper,
        F1_indianapolis_only_constructors_list_scraper,
        F1_privateer_teams_list_scraper,
    )
    from scrapers.drivers import F1_drivers_list_scraper  # noqa: F401
    from scrapers.engines import (  # noqa: F401
        F1_engine_manufacturers_list_scraper,
        F1_indianapolis_only_engine_manufacturers_list_scraper,
    )
    from scrapers.grands_prix import F1_grands_prix_list_scraper  # noqa: F401
    from scrapers.seasons import F1_seasons_list_scraper  # noqa: F401
