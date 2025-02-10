from __future__ import annotations
from enum import Enum
from typing import TypeAlias,Callable,Type
import typing
from nexios.http import Request,Response
from nexios.websockets import WebSocket
from typing_extensions import Doc
class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    
AppType = typing.TypeVar("AppType")

Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]
    
MiddlewareType :TypeAlias = Callable[[Type[Request],Type[Response],Type[Callable]], Type[Response]]
WsMiddlewareType :TypeAlias = Callable[[Type[WebSocket],Type[Callable]], Type[Send]]



ASGIApp = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]

