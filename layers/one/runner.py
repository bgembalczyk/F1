"""Preferred naming alias for layer-one orchestration.

`LayerOneExecutor` remains supported for backwards compatibility.
"""

from layers.one.executor import LayerOneExecutor

LayerOneRunner = LayerOneExecutor

__all__ = ["LayerOneRunner"]
