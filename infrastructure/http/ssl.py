import ssl
from collections.abc import Callable

import certifi


def build_ssl_context() -> ssl.SSLContext:
    """Builds the default SSL context using certifi CA store."""
    context = ssl.create_default_context(cafile=certifi.where())
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context


SSLContextProvider = Callable[[], ssl.SSLContext]
