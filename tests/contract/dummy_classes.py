class StubFetcher:
    def __init__(self, html: str) -> None:
        self.html = html
        self.calls = 0

    def get_text(self, _url: str, *, _timeout: int | None = None) -> str:
        self.calls += 1
        return self.html

    def get(self, url: str) -> str:
        return self.get_text(url)
