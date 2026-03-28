import ssl

import certifi

HTTP_BAD_REQUEST = 400

ALLOWED_URL_SCHEMES = {"http", "https"}

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
