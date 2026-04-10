import warnings

from scrapers.core import infobox as core_infobox

warnings.warn(
    "scrapers.legacy.infobox is deprecated; use scrapers.core.infobox",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["core_infobox"]
