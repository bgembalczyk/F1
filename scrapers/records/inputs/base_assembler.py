from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from models.wiki_url import WikiUrl


@dataclass(frozen=True)
class BaseRecordAssemblerInput:
    """Unified input model for assembling export records."""

    url: WikiUrl | str | None = None
    metadata: Mapping[str, Any] | None = None
    infobox: Mapping[str, Any] | None = None
    infoboxes: list[Mapping[str, Any]] | None = None
    sections: list[dict[str, Any]] | None = None
    tables: list[dict[str, Any]] | None = None
