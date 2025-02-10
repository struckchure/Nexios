from __future__ import annotations
from enum import Enum
from typing import TypeAlias,Callable,Type,Awaitable
import typing
from nexios.http import Request,Response
from nexios.websockets import WebSocket
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
    
MiddlewareType :TypeAlias = Callable[[Type[Request],Type[Response],Type[Callable[...,Awaitable[Response | None]]]], Type[Response]] 
WsMiddlewareType :TypeAlias = Callable[[Type[WebSocket],Type[Callable[...,Awaitable[Message]]]], Type[Send]]  

WsHandlerType = Callable[..., Awaitable[Send | Message]]
HandlerType = Callable[..., Awaitable[Response]]
ExceptionHandlerType = Callable[[Type[Request],Type[Response]],typing.Any[Awaitable[Response],None]]

ASGIApp = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]

