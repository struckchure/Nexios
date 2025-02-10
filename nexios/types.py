from enum import Enum
from typing import TypeAlias,Callable,Type
from nexios.http import Request,Response
from typing_extensions import Doc
class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    
    
MiddlewareType :TypeAlias = Callable[[Type[Request],Type[Response],Type[Callable]], Type[Response]]

