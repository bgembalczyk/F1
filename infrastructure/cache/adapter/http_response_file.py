from infrastructure.cache.adapter.file_ttl import FileTtlCacheAdapter


class HttpResponseFileCacheAdapter(FileTtlCacheAdapter[str]):
    """Adapter cache dla tekstowej odpowiedzi HTTP."""

    extension = ".html"

    def serialize(self, value: str) -> str:
        return value

    def deserialize(self, raw_text: str) -> str:
        return raw_text
