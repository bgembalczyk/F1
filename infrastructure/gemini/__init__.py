"""Public API for Gemini infrastructure integrations.

Everything outside this module's ``__all__`` should be treated as internal.
"""

from importlib import import_module
from typing import TYPE_CHECKING
from typing import Any

from infrastructure.gemini.constants import DEFAULT_MODELS
from infrastructure.gemini.constants import DEFAULT_TIMEOUT

if TYPE_CHECKING:
    from infrastructure.gemini.client import GeminiClient
    from infrastructure.gemini.model_config import ModelConfig
    from infrastructure.gemini.model_state import ModelState

__all__ = [
    "DEFAULT_MODELS",
    "DEFAULT_TIMEOUT",
    "GeminiClient",
    "ModelConfig",
    "ModelState",
]


def __getattr__(name: str) -> Any:
    if name == "GeminiClient":
        return import_module("infrastructure.gemini.client").GeminiClient
    if name == "ModelConfig":
        return import_module("infrastructure.gemini.model_config").ModelConfig
    if name == "ModelState":
        return import_module("infrastructure.gemini.model_state").ModelState
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
