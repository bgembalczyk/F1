"""Base class for infobox field parsers."""


class BaseInfoboxFieldParser:
    """Base class for infobox field parsers.

    Subclasses should implement a ``parse`` method that accepts a raw input
    value (typically a ``bs4.Tag`` or ``str``) and returns the parsed result.
    Static and instance method variants are both supported.
    """


__all__ = ["BaseInfoboxFieldParser"]
