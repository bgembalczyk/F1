class HttpShimErrorResponseAdapter:
    """Adapter utrzymujący kompatybilność z obiektami typu requests.Response."""

    def __init__(self, error: "HttpShimError") -> None:
        self.url = error.url
        self.status_code = error.status_code
        self.headers = error.headers
        self.text = error.body

    def raise_for_status(self) -> None:
        """Interfejs zgodny z requests.Response; błąd jest już podniesiony."""
        return


__all__ = ["HttpShimErrorResponseAdapter"]
