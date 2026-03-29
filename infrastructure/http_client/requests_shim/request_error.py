from collections.abc import Mapping


class RequestError(Exception):
    """Bazowy błąd requests_shim zgodny z kontraktem HTTP error."""

    def __init__(
        self,
        reason: str,
        *,
        url: str = "",
        status: int = 0,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(reason)
        self.url = str(url)
        self.status = int(status)
        self.reason = str(reason)
        self.headers = {str(k): str(v) for k, v in (headers or {}).items()}

    @property
    def status_code(self) -> int:
        """Kompatybilność wsteczna z semantyką response/status_code."""
        return self.status
