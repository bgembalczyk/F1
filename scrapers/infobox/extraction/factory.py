from __future__ import annotations

from typing import Any

from scrapers.infobox.extraction.registry import ORCHESTRATOR_REGISTRY
from scrapers.options import ScraperOptions


def build_infobox_orchestrator(
    domain: str,
    *,
    options: ScraperOptions | None = None,
    **kwargs: Any,
) -> Any:
    try:
        orchestrator_cls = ORCHESTRATOR_REGISTRY[domain]
    except KeyError as exc:
        available = ", ".join(sorted(ORCHESTRATOR_REGISTRY))
        raise ValueError(f"Unknown infobox domain: {domain!r}. Available: {available}") from exc
    return orchestrator_cls(options=options, **kwargs)
