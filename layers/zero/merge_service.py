from collections.abc import Callable
from pathlib import Path

from layers.orchestration.contracts import LayerZeroMergeRequestDTO
from layers.orchestration.contracts import LayerZeroMergeResultDTO


class LayerZeroMergeService:
    def __init__(self, *, merge_function: Callable[[Path], None]) -> None:
        self._merge_function = merge_function

    def merge(
        self,
        request: LayerZeroMergeRequestDTO | Path,
    ) -> LayerZeroMergeResultDTO:
        request_dto = (
            request
            if isinstance(request, LayerZeroMergeRequestDTO)
            else LayerZeroMergeRequestDTO(base_wiki_dir=request)
        )
        request_dto.validate()
        self._merge_function(request_dto.base_wiki_dir)
        return LayerZeroMergeResultDTO(merged=True)
