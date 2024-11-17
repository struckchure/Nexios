import json
from typing import Any, Dict, Optional, Union, List, AsyncGenerator, Callable, Tuple,Protocol
from urllib.parse import urlparse, urlunparse
from ..structs import URL
from .cookies_parser import parse_cookies
from .parsers import parse_multipart_data
from nexio.contrib.sessions.backends.base import SessionBase
class RequestExtraType(Protocol):
    session: SessionBase
class ClientDisconnect(Exception, RequestExtraType):
    """Custom exception to indicate client disconnection."""
    pass

# Utility Functions


def parse_query_string(query_string: str) -> Dict[str, str]:
    """Parses a query string into a dictionary of key-value pairs."""
    params = {}
    for param in query_string.split("&"):
        if "=" in param:
            key, value = param.split("=", 1)
            params[key] = value
        else:
            params[param] = ""
    return params

def parse_form_data(body: str) -> Dict[str, str]:
    """Parses 'application/x-www-form-urlencoded' data into a dictionary of key-value pairs."""
    form_data = {}
    for pair in body.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            form_data[key] = value
    return form_data

def parse_content_type(content_type_header: str) -> Tuple[str, Dict[str, str]]:
    """Parses the 'Content-Type' header into MIME type and any additional parameters."""
    main_type, *params = content_type_header.split(";")
    params_dict = {}
    for param in params:
        if "=" in param:
            key, value = param.strip().split("=", 1)
            params_dict[key] = value
    return main_type.strip(), params_dict

def get_user_agent_details(user_agent: str) -> Dict[str, str]:
    """Extracts basic details from the User-Agent header."""
    details = {"browser": "Unknown", "os": "Unknown"}
    if "Chrome" in user_agent:
        details["browser"] = "Chrome"
    elif "Firefox" in user_agent:
        details["browser"] = "Firefox"
    elif "Safari" in user_agent:
        details["browser"] = "Safari"

    if "Windows" in user_agent:
        details["os"] = "Windows"
    elif "Macintosh" in user_agent:
        details["os"] = "macOS"
    elif "Linux" in user_agent:
        details["os"] = "Linux"
    return details

# HTTP Connection Classes

class HTTPConnection:
    """Base class for managing HTTP connections, including headers, cookies, and client details."""
    def __init__(self, scope: Dict[str, Any]) -> None:
        self.scope = scope


        
    @property
    def url(self) -> URL:
        return URL(scope=self.scope)

    def build_absolute_uri(self, path: Optional[str] = None) -> str:
        """Builds the absolute URI, similar to Django's `build_absolute_uri`."""
        base_url = self.url.rsplit("?", 1)[0]  # Remove query if exists
        if path:
            return f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        return base_url

    @property
    def headers(self) -> Dict[str, str]:
        """Parses and returns headers as a dictionary."""
        return {name.decode(): value.decode() for name, value in self.scope.get("headers", [])}

    @property
    def cookies(self) -> Dict[str, str]:
        """Parses and returns cookies from headers."""
        cookie_header = self.headers.get("cookie", "")
        return parse_cookies(cookie_header)

    @property
    def content_type(self) -> str:
        """Returns the MIME type of the request content."""
        content_type, _ = parse_content_type(self.headers.get("content-type", ""))
        return content_type

    @property
    def client(self) -> Optional[str]:
        """Returns client information as a tuple of (host, port)."""
        return self.scope.get("client")

    def get_header(self, name: str) -> Optional[str]:
        """Fetches a single header by name, case-insensitive."""
        return self.headers.get(name.lower())

    @property
    def user_agent(self) -> str:
        """Returns the User-Agent header if available."""
        return self.headers.get("user-agent", "")

    @property
    def meta(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """Returns request metadata, including headers, cookies, and user-agent details."""
        return {
            "headers": self.headers,
            "cookies": self.cookies,
            "content_type": self.content_type,
            "user_agent_details": get_user_agent_details(self.user_agent)
        }

class Request(HTTPConnection):
    """Handles HTTP request data, including methods for handling body, JSON, and form data."""
    def __init__(self, scope: Dict[str, Any], receive: Callable[[], bytes], send:Callable) -> None:
        super().__init__(scope)
        self._receive = receive
        self._body = None
        self._json = None
        self._form_data = None

    @property
    def method(self) -> str:
        """Returns the HTTP method (GET, POST, etc.)."""
        return self.scope["method"]

    async def body(self) -> bytes:
        """Asynchronously retrieves the request body."""
        if self._body is None:
            self._body = b""
            message = await self._receive()
            if message["type"] == "http.request":
                self._body += message.get("body", b"")
        return self._body

    async def json(self) -> Any:
        """Parses and returns JSON data from the body."""
        if self._json is None:
            body = await self.body()
            self._json = json.loads(body)
        return self._json

    async def form_data(self) -> Dict[str, str]:
        """Parses and returns form data from the body."""
        if self._form_data is None:
            body = await self.body()
            body_str = body.decode("utf-8")
            self._form_data = parse_form_data(body_str)
        return self._form_data

    async def stream(self) -> AsyncGenerator[bytes, None]:
        """Asynchronously yields chunks of the request body for streaming."""
        message = await self._receive()
        if message["type"] == "http.request":
            yield message.get("body", b"")
        elif message["type"] == "http.disconnect":
            raise ClientDisconnect()

    async def is_disconnected(self) -> bool:
        """Checks if the client has disconnected."""
        message = await self._receive()
        return message.get("type") == "http.disconnect"
    @property
    async def files(self):
        return await parse_multipart_data(self)
    

    

    
    