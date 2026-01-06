"""Base class for parsers with safe error handling."""

from typing import Any, Callable, Optional, TypeVar

from scrapers.base.error_handler import ErrorHandler
from scrapers.base.errors import ScraperError

_T = TypeVar("_T")


class SafeParserMixin:
    """
    Mixin class providing safe parsing functionality.
    
    Classes that use this mixin should have:
    - self.error_handler: ErrorHandler instance
    - self._url_provider: Optional[Callable[[], Optional[str]]] for getting the current URL
    """

    def _safe_parse(
        self,
        fn: Callable[..., _T],
        *args: Any,
        **kwargs: Any,
    ) -> Optional[_T]:
        """
        Safely executes a parsing function, handling errors gracefully.

        If an error occurs, it's wrapped and passed to the error handler.
        If the error handler indicates the error can be ignored, returns None.
        Otherwise, re-raises the error.

        Args:
            fn: The parsing function to execute.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            The result of the function call, or None if an error occurred and was handled.

        Raises:
            Exception: If the error handler indicates the error should not be ignored.
        """
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            url = self._url_provider() if self._url_provider else None
            error = (
                exc
                if isinstance(exc, ScraperError)
                else self.error_handler.wrap_parse(exc, url=url)
            )
            if self.error_handler.handle(error):
                return None
            if error is exc:
                raise
            raise error from exc
