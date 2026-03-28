from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Generic
from typing import TypeVar

if TYPE_CHECKING:
    from models.value_objects import WikiUrl
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter


ServiceT = TypeVar("ServiceT")


class ValidatingSectionServiceFactory(Generic[ServiceT]):
    """Shared dependency validation for section service factories."""

    def _validate_dependencies(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None,
        url: WikiUrl | str | None,
        require_options: bool,
        require_url: bool,
    ) -> None:
        if adapter is None:
            msg = "SectionAdapter dependency is required."
            raise ValueError(msg)

        if require_options and options is None:
            msg = "ScraperOptions dependency is required for this section service."
            raise ValueError(msg)

        if require_url and not url:
            msg = "Article URL dependency is required for this section service."
            raise ValueError(msg)
