from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.run_config_factories.contracts import LayerZeroRunConfigFactory


class DefaultLayerZeroRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(
        self,
        job: ListJobRegistryEntry | None = None,
    ) -> dict[str, object]:
        _ = job
        return {}
