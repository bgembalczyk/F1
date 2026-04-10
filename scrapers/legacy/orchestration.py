import warnings

from scrapers.core import orchestration as core_orchestration

warnings.warn(
    "scrapers.legacy.orchestration is deprecated; use scrapers.core.orchestration",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["core_orchestration"]
