import inspect

from scrapers.base.abc import ABCScraper


class ConstructorIntrospection:
    def __init__(self, scraper_cls: type[ABCScraper]) -> None:
        self._signature = inspect.signature(scraper_cls.__init__)
        self._parameters = self._signature.parameters

    def accepts(self, param_name: str) -> bool:
        if param_name in self._parameters:
            return True
        return any(
            param.kind == inspect.Parameter.VAR_KEYWORD
            for param in self._parameters.values()
        )

    def accepts_explicitly(self, param_name: str) -> bool:
        return param_name in self._parameters
