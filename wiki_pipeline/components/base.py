from typing import NamedTuple

from layers.executors.one import LayerOneExecutor
from layers.executors.zero import LayerZeroExecutor
from layers.zero.merge_service import LayerZeroMergeService


class WikiPipelineComponents(NamedTuple):
    layer_zero_executor: LayerZeroExecutor
    layer_one_executor: LayerOneExecutor
    layer_zero_merge_service: LayerZeroMergeService
