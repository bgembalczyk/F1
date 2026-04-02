"""Preferred naming alias for layer-zero orchestration.

`LayerZeroExecutor` remains supported for backwards compatibility.
"""

from layers.zero.executor import LayerZeroExecutor

LayerZeroRunner = LayerZeroExecutor

__all__ = ["LayerZeroRunner"]
