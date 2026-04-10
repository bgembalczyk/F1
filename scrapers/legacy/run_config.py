import warnings

from scrapers.core.run_config import RunConfig

warnings.warn(
    "scrapers.legacy.run_config is deprecated; use scrapers.core.run_config",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["RunConfig"]
