from infrastructure.http_client.requests_shim.request_error import RequestError


class HTTPTimeoutError(RequestError):
    pass
