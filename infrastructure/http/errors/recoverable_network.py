from infrastructure.http.errors.base import RequestError

RecoverableNetworkError = (
    RequestError,
    ConnectionError,
    OSError,
    TimeoutError,
)
