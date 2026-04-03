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


class ConfigurableSectionServiceFactory(
    ValidatingSectionServiceFactory[ServiceT],
    Generic[ServiceT],
):
    """Generic section-service factory replacing per-domain pass-through wrappers."""

    def __init__(
        self,
        *,
        service_cls: type[ServiceT],
        require_options: bool,
        require_url: bool,
        pass_options: bool = True,
        pass_url: bool = True,
    ) -> None:
        self._service_cls = service_cls
        self._require_options = require_options
        self._require_url = require_url
        self._pass_options = pass_options
        self._pass_url = pass_url

    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: WikiUrl | str | None = None,
    ) -> ServiceT:
        self._validate_dependencies(
            adapter=adapter,
            options=options,
            url=url,
            require_options=self._require_options,
            require_url=self._require_url,
        )
        kwargs = {"adapter": adapter}
        if self._pass_options:
            kwargs["options"] = options
        if self._pass_url:
            kwargs["url"] = url
        return self._service_cls(**kwargs)  # type: ignore[call-arg]
