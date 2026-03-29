from collections.abc import Callable
import ssl

import certifi


def build_ssl_context() -> ssl.SSLContext:
    """Builds the default SSL context using certifi CA store."""
    return ssl.create_default_context(cafile=certifi.where())


SSLContextProvider = Callable[[], ssl.SSLContext]
