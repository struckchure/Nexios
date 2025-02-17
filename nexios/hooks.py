
from functools import wraps, lru_cache
import asyncio
import time, re
from typing import Callable, Optional, Awaitable, List, Any, Dict
from nexios.http import Request, Response

HandlerType = Callable[..., Awaitable[Response]]


def before_request(
    func: Optional[Callable[[Request, Response], Any]],
    *,
    log_level: Optional[str] = None,
    only_methods: Optional[List[str]] = None,
    for_routes: Optional[str] = None,
) -> None:
    """
    A decorator for before_request hooks with advanced options.

    :param func: The function to run before the request.
    :param log_level: Logging level for the hook (e.g., "INFO", "DEBUG").
    :param only_methods: A list of HTTP methods to apply the hook (e.g., ["POST", "GET"]).
    :param for_routes: A list of specific routes to apply the hook (e.g., ["/api/create/{id}"].
    """

    def decorator(handler: HandlerType) -> HandlerType:
        @wraps(handler)
        async def wrapper(*args: List[Any], **kwargs: Dict[str, Any]):
            req: Request = args[-2]  # type: ignore
            res: Response = args[-1]  # type: ignore

            if only_methods and req.method.upper() not in map(str.upper, only_methods):
                return await handler(*args, **kwargs)
            if for_routes and req.url.path not in for_routes:
                return await handler(*args, **kwargs)
            if log_level:
                print(f"[{log_level}] Before Request: {req.method} {req.url}")
            if func:
                await func(req, res)
            return await handler(*args, **kwargs)

        return wrapper

    return decorator  # type:ignore


def after_request(
    func: Optional[Callable[[Request, Response], Any]],
    *,
    log_level: Optional[str] = None,
    only_methods: Optional[List[str]] = None,
    for_routes: Optional[List[str]] = None,
) -> None:
    """
    A decorator for after_request hooks with advanced options.

    :param func: The function to run after the request.
    :param log_level: Logging level for the hook (e.g., "INFO", "DEBUG").
    :param only_methods: A list of HTTP methods to apply the hook (e.g., ["POST", "GET"]).
    :param for_routes: A list of specific routes to apply the hook (e.g., ["/api/create/{id}"].
    """

    def decorator(handler: HandlerType) -> HandlerType:
        @wraps(handler)
        async def wrapper(*args: List[Any], **kwargs: Dict[str, Any]):
            req: Request = args[-2]  # type:ignore
            res: Response = args[-2]  # type:ignore

            response: Response = await handler(*args, **kwargs)
            if only_methods and req.method.upper() not in map(str.upper, only_methods):
                return response
            if for_routes and req.url.path not in for_routes:
                return response
            if log_level:
                print(
                    f"[{log_level}] After Request: {req.method} {req.url} - Status: {response._status_code}"
                )  # type: ignore
            if func:
                await func(req, response)
            return response

        return wrapper

    return decorator  # type:ignore


def analytics(func: HandlerType) -> HandlerType:
    """
    A decorator to track analytics for an endpoint.
    """

    @wraps(func)
    async def wrapper(*args: List[Any], **kwargs: Dict[str, Any]):
        req: Request = args[-2]  # type:ignore
        res: Response = args[-1]  # type:ignore
        start_time = time.time()
        response = await func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(
            f"Analytics: {req.method} {req.url} - {response._status_code} in {elapsed_time:.2f}s"
        )  # type:ignore
        return response

    return wrapper


def cache_response(max_size: int = 128):
    """
    A decorator to cache responses in memory.
    """

    def decorator(handler: HandlerType):
        cached_func = lru_cache(maxsize=max_size)(handler)
        return cached_func

    return decorator


def maintenance_mode(is_maintenance: bool = True):
    """
    A decorator to restrict access during maintenance.

    :param is_maintenance: Boolean to enable or disable maintenance mode.
    """

    def decorator(handler: HandlerType) -> HandlerType:
        @wraps(handler)
        async def wrapper(*args: List[Any], **kwargs: Dict[str, Any]):
            res: Response = args[-1]  # type: ignore
            if is_maintenance:
                return res.json(
                    {"error": "Service unavailable due to maintenance"}, status_code=503
                )  # type: ignore #TODO:ad custom handler
            return await handler(*args, **kwargs)

        return wrapper

    return decorator


def request_timeout(timeout: int):
    """
    A decorator to enforce request timeouts.

    :param timeout: Timeout duration in seconds.
    """

    def decorator(handler: HandlerType) -> HandlerType:
        @wraps(handler)
        async def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Response:
            res: Response = args[-1]  # type:ignore
            try:
                return await asyncio.wait_for(handler(*args, **kwargs), float(timeout))
            except asyncio.TimeoutError:
                return res.json({"error": "Request timed out"}, status_code=408)

        return wrapper

    return decorator


def capture_request_metadata(log_func: Callable[..., Awaitable[Response]]) -> None:
    """
    A decorator to log request metadata for analysis.

    :param log_func: A function to handle the metadata.
    """

    def decorator(handler: HandlerType) -> HandlerType:
        @wraps(handler)
        async def wrapper(*args: List[Any], **kwargs: Dict[str, Any]):
            req: Request = args[-2]  # type:ignore
            metadata: Dict[str, Any] = {
                "method": req.method,
                "url": str(req.url),
                "headers": dict(req.headers),
                "client_ip": req.client.host,  # type:ignore
            }
            log_func(metadata)
            return await handler(*args, **kwargs)

        return wrapper

    return decorator  # type:ignore


def use_for_route(route: str) -> None:
    if route.endswith("/*"):
        route = route[:-2]
        route = f"^{route}/.*$"
    else:
        route = f"^{route}$"

    def decorator(func: HandlerType) -> HandlerType:
        @wraps(func)
        async def wrapper_func(
            request: Request,
            response: Response,
            call_next: Callable[..., Awaitable[Response]],
        ):
            if re.match(route, request.url.path):
                return await func(request, response, call_next)
            else:
                return await call_next()

        @wraps(func)
        async def wrapper_klass(
            self: Any,
            request: Request,
            response: Response,
            call_next: Callable[..., Awaitable[Response]],
        ):
            if re.match(route, request.url.path):
                return await func(self, request, response, call_next)
            else:
                return await call_next()

        if func.__name__ == "__call__":
            return wrapper_klass
        else:
            return wrapper_func

    return decorator  # type:ignore
