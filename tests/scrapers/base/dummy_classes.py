from scrapers.single_wiki_article import SectionByIdScraperBase
from scrapers.source_adapter import SourceAdapter


class ConcreteSectionByIdScraper(SectionByIdScraperBase):
    """Minimal concrete subclass for testing."""

    def _assemble_record(self, *_args, **_kwargs):
        return {}


class StubHttpClient:
    def __init__(self, response: str = "page content") -> None:
        self._response = response
        self.calls: list[tuple[str, int | None]] = []

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        self.calls.append((url, timeout))
        return self._response


class MemoryCache:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def set(self, key: str, value: str) -> None:
        self.store[key] = value

class FailingParser:
    def parse(self, _soup):
        msg = "boom"
        raise ValueError(msg)

    def find_infobox(self, soup):
        return soup.find("table", class_="infobox")


class PassThroughMapper:
    def map(self, raw):
        return raw


class MemoryCache2:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}
        self.get_calls = 0
        self.set_calls = 0

    def get(self, key: str) -> str | None:
        self.get_calls += 1
        return self.store.get(key)

    def set(self, key: str, value: str) -> None:
        self.set_calls += 1
        self.store[key] = value


class StubSourceAdapter(SourceAdapter):
    def __init__(self) -> None:
        self.calls = 0

    @property
    def metadata(self) -> dict[str, object]:
        return {"source": "stub"}

    def get(self, url: str) -> str:
        self.calls += 1
        return f"fresh:{url}:{self.calls}"


class ReadErrorCache(MemoryCache):
    def get(self, _key: str) -> str | None:
        msg = "cache read failed"
        raise OSError(msg)


class WriteErrorCache(MemoryCache):
    def set(self, _key: str, _value: str) -> None:
        msg = "cache write failed"
        raise OSError(msg)


