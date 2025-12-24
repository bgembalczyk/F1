from infrastructure.http_client.requests_shim.request_exception import RequestException


class Timeout(RequestException):
    pass
