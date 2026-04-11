import ssl
from collections.abc import Callable
from os import getenv

import certifi


def build_ssl_context() -> ssl.SSLContext:
    """Builds the default SSL context using certifi CA store."""
    if getenv("F1_HTTP_INSECURE_SSL", "").lower() in {"1", "true", "yes", "on"}:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        return context

    context = ssl.create_default_context(cafile=certifi.where())
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context


SSLContextProvider = Callable[[], ssl.SSLContext]
