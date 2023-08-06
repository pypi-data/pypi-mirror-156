from typing import Any, Tuple, final

from trio import TooSlowError

__all__ = (
    "ClientError",
    "ConnectionError",
    "UnclosedClient",
    "UnclosedConnector",
    "UnclosedConnection",
    "UnclosedResponse",
    "ConnectionTimeout",
    "WriteTimeout",
    "ReadTimeout",
    "ConnectionOSError",
    "ProxyConnectionTimeout",
    "ProxyError",
    "ProxyConnectionError",
    "ConnectionSSLError",
    "ProxyConnectionSSLError",
    "InvalidURL",
    "InvalidProxy",
    "MalformedResponse",
    "MaxRedirect",
)


class ClientError(Exception):
    """Base class for all client errors"""

    __slots__ = ()


class ConnectionError(Exception):
    """Base class for all connection errors"""

    __slots__ = ()


@final
class UnclosedClient(ClientError, RuntimeError):
    """A client was not closed"""

    __slots__ = ()

    def __str__(self) -> str:
        return "Unclosed client"


@final
class UnclosedConnector(ClientError, RuntimeError):
    """A client was not closed"""

    __slots__ = ()

    def __str__(self) -> str:
        return "Unclosed connector"


@final
class UnclosedConnection(ConnectionError, RuntimeError):
    """The underlying connection was not closed"""

    __slots__ = ()

    def __str__(self) -> str:
        return "Unclosed connection"


@final
class UnclosedResponse(ClientError, RuntimeError):
    """The response was not closed"""

    __slots__ = ()

    def __str__(self) -> str:
        return "Unclosed response"


@final
class RequestTimeout(ClientError):
    """The request exceed the given deadline"""

    __slots__ = ()

    def __str__(self) -> str:
        return "The request exceed the given deadline"


class ConnectionTimeout(ConnectionError, TooSlowError):
    """The connect attempt exceeded the given timeout"""

    __slots__ = ()

    def __str__(self) -> str:
        return "The server took too long to respond"


@final
class WriteTimeout(ConnectionError, TooSlowError):
    """The write attempt exceeded the given timeout"""

    __slots__ = ()

    def __str__(self) -> str:
        return "Writing took too long"


@final
class ReadTimeout(ConnectionError, TooSlowError):
    """The read attempt exceeded the given timeout"""

    __slots__ = ()

    def __str__(self) -> str:
        return "Reading took too long"


class ConnectionOSError(ConnectionError):
    """The connect attempt failed"""

    __slots__: Tuple[str, str, str] = ("host", "port", "os_error")

    def __init__(self, host: Any, port: Any, os_error: OSError) -> None:
        self.host = host
        self.port = port
        self.os_error = os_error

    def __str__(self) -> str:
        return f"Cannot connect to host {self.host}:{self.port} [{self.os_error.errno}: {self.os_error.strerror}]"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} host={self.host} port={self.port} os_error={self.os_error}>"


@final
class ProxyConnectionTimeout(ConnectionTimeout):
    """The proxy connect attempt exceeded the given timeout"""

    __slots__ = ()

    def __str__(self) -> str:
        return "The proxy took too long to respond"


class ProxyError(ConnectionError):
    """The proxy returned an unusual response"""

    __slots__: Tuple[str, str] = ("status", "reason")

    def __init__(self, status: int, reason: str) -> None:
        self.status = status
        self.reason = reason

    def __str__(self) -> str:
        return f"{self.status}: {self.reason}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} status={self.status} status={self.reason}>"


@final
class ProxyConnectionError(ConnectionOSError):
    """The proxy connect attempt failed"""

    __slots__ = ()


class ConnectionSSLError(ConnectionError):

    __slots__: Tuple[str, str, str] = (
        "library",
        "reason",
        "message",
    )

    def __init__(self, library: str, reason: str, message: str) -> None:
        self.library = library
        self.reason = reason
        self.message = message

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} library={self.library} reason={self.reason}>"
        )

    def __str__(self) -> str:
        return f"[{self.library}: {self.reason}]: {self.message}"


@final
class ProxyConnectionSSLError(ConnectionSSLError):
    """The proxy connect attempt failed"""

    __slots__ = ()


class InvalidURL(ClientError, ValueError):
    """Malformed url"""

    __slots__: Tuple[str] = ("url",)

    def __init__(self, url: Any) -> None:
        self.url = url

    def __str__(self) -> Any:
        return self.url

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.url}>"


@final
class InvalidProxy(InvalidURL):
    """Malformed proxy"""

    __slots__ = ()


class MalformedResponse(ClientError):
    """Malformed HTTP response"""

    __slots__: Tuple[str] = ("error",)

    def __init__(self, error: str) -> None:
        self.error = error

    def __str__(self) -> str:
        return self.error

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} error={self.error}>"


class MaxRedirect(ClientError):
    """Maximum amount of redirects reached"""

    __slots__: Tuple[str, str] = ("last_url", "amount")

    def __init__(self, last_url: str, amount: int, *args: object) -> None:
        self.last_url = last_url
        self.amount = amount
        super().__init__(*args)

    def __str__(
        self,
    ) -> str:
        return f"Maximum amount of redirects reached: {self.amount}"

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} last_url={self.last_url} amount={self.amount}>"
        )
