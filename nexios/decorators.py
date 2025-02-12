from typing import List, Dict, Any
from .http.request import Request
from .http.response import NexioResponse
from .http.request import Request
import typing
from functools import wraps
from .types import HandlerType


class RouteDecorator:
    """Base class for all route decorators"""

    def __init__(self, **kwargs: Dict[str, Any]):
        pass

    async def __call__(self, handler: HandlerType) -> Any:
        raise NotImplementedError("Handler not set")

    def __get__(self, obj: typing.Any, objtype: typing.Any = None):
        if obj is None:
            return self
        return self.__class__(obj)  # type:ignore


class allowed_methods(RouteDecorator):
    def __init__(self, methods: List[str]):
        super().__init__()
        self.allowed_methods = [method.upper() for method in methods]
        self.allowed_methods.extend(["OPTIONS"])

    def __call__(self, handler: HandlerType) -> Any:
        @wraps(handler)
        async def wrapper(request: Request, response: NexioResponse):
            if request.method.upper() not in self.allowed_methods:
                return response.json(
                    {
                        "error": f"Method {request.method} not allowed",
                        "allowed_methods": self.allowed_methods,
                    },
                    status_code=405,
                )
            return await handler(request, response)

        return wrapper
