from scrapers.columns.context import ColumnContext


class ConstructorPartParser:
    def __init__(self, index: int) -> None:
        raise NotImplementedError

    def parse(self, ctx: ColumnContext) -> dict[str, object] | None:
        raise NotImplementedError


ConstructorPartParserABC = ConstructorPartParser

__all__ = ["ConstructorPartParser", "ConstructorPartParserABC"]
