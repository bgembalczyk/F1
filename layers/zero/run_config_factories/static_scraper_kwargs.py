from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.run_config_factories.contracts import LayerZeroRunConfigFactory


class StaticScraperKwargsFactory(LayerZeroRunConfigFactory):
    def __init__(self, *, scraper_kwargs: dict[str, object]) -> None:
        self._scraper_kwargs = dict(scraper_kwargs)

    def create_scraper_kwargs(
        self,
        job: ListJobRegistryEntry | None = None,
    ) -> dict[str, object]:
        _ = job
        return dict(self._scraper_kwargs)
