"""HTTP utilities including client interfaces and shims."""

from .interfaces import HttpClientProtocol, HttpResponseProtocol
from . import requests_shim

__all__ = ["HttpClientProtocol", "HttpResponseProtocol", "requests_shim"]
