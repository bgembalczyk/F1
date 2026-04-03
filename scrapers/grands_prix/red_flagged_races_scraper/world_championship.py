"""Legacy CLI adapter for world championship red-flagged races scraper."""

from scrapers.grands_prix.red_flagged_races_scraper.services.world_championship import (
    RedFlaggedWorldChampionshipRacesScraper,
)

__all__ = ["RedFlaggedWorldChampionshipRacesScraper"]


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
