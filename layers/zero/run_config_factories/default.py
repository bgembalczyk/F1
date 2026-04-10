from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.run_config_factories.base import LayerZeroRunConfigFactory


class DefaultLayerZeroRunConfigFactory(LayerZeroRunConfigFactory):
    role = "run_config_factory"
    domain = "default"
    stage = "layer_zero"

    def create_scraper_kwargs(
        self,
        job: ListJobRegistryEntry | None = None,
    ) -> dict[str, object]:
        _ = job
        return {}
