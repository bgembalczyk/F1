"""Public API for Gemini infrastructure integrations.

Everything outside this module's ``__all__`` should be treated as internal.
"""

from infrastructure.gemini.constants import DEFAULT_MODELS
from infrastructure.gemini.constants import DEFAULT_TIMEOUT
from infrastructure.gemini.model_config import ModelConfig
from infrastructure.gemini.model_state import ModelState


def __getattr__(name: str):
    if name == "GeminiClient":
        # Lazy import avoids circular dependency during config bootstrap.
        from infrastructure.gemini.client import GeminiClient

        return GeminiClient
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


__all__ = [
    "DEFAULT_MODELS",
    "DEFAULT_TIMEOUT",
    "GeminiClient",
    "ModelConfig",
    "ModelState",
]
