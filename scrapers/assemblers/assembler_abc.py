from abc import ABC


class AssemblerABC(ABC):
    """Canonical assembler contract.

    All assemblers must implement an ``assemble`` method that transforms
    a domain payload into an exportable mapping. The exact signature of
    ``assemble`` varies per assembler due to differing payload types, so
    the method is not enforced as abstract here.
    """


__all__ = ["AssemblerABC"]
