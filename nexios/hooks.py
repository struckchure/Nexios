from functools import wraps, lru_cache
import asyncio
import time,re
from typing import Callable

def before_request(func=None, *, log_level=None, only_methods=None, for_routes=None):
    """
    A decorator for before_request hooks with advanced options.

    :param func: The function to run before the request.
    :param log_level: Logging level for the hook (e.g., "INFO", "DEBUG").
    :param only_methods: A list of HTTP methods to apply the hook (e.g., ["POST", "GET"]).
    :param for_routes: A list of specific routes to apply the hook (e.g., ["/api/create/{id}"].
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(*args, **kwargs):
            req, res = args[-2], args[-1]
            if only_methods and req.method.upper() not in map(str.upper, only_methods):
                return await handler(*args, **kwargs)
            if for_routes and req.url.path not in for_routes:
                return await handler(*args, **kwargs)
            if log_level:
                print(f"[{log_level}] Before Request: {req.method} {req.url}")
            if func:
                await func(req)
            return await handler(*args, **kwargs)
        return wrapper
    return decorator

def after_request(func=None, *, log_level=None, only_methods=None, for_routes=None):
    """
    A decorator for after_request hooks with advanced options.

    :param func: The function to run after the request.
    :param log_level: Logging level for the hook (e.g., "INFO", "DEBUG").
    :param only_methods: A list of HTTP methods to apply the hook (e.g., ["POST", "GET"]).
    :param for_routes: A list of specific routes to apply the hook (e.g., ["/api/create/{id}"].
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(*args, **kwargs):
            req, res = args[-2], args[-1]
            response = await handler(*args, **kwargs)
            if only_methods and req.method.upper() not in map(str.upper, only_methods):
                return response
            if for_routes and req.url.path not in for_routes:
                return response
            if log_level:
                print(f"[{log_level}] After Request: {req.method} {req.url} - Status: {response._status_code}")
            if func:
                await func(req, response)
            return response
        return wrapper
    return decorator

def analytics(func):
    """
    A decorator to track analytics for an endpoint.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        req, res = args[-2], args[-1]
        start_time = time.time()
        response = await func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"Analytics: {req.method} {req.url} - {response._status_code} in {elapsed_time:.2f}s")
        return response
    return wrapper

def cache_response(max_size=128):
    """
    A decorator to cache responses in memory.
    """
    def decorator(handler):
        cached_func = lru_cache(maxsize=max_size)(handler)
        return cached_func
    return decorator

def maintenance_mode(is_maintenance):
    """
    A decorator to restrict access during maintenance.

    :param is_maintenance: Boolean to enable or disable maintenance mode.
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(*args, **kwargs):
            req, res = args[-2], args[-1]
            if is_maintenance:
                return res.json({"error": "Service unavailable due to maintenance"}, status_code=503)
            return await handler(*args, **kwargs)
        return wrapper
    return decorator

def request_timeout(timeout):
    """
    A decorator to enforce request timeouts.

    :param timeout: Timeout duration in seconds.
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(*args, **kwargs):
            req, res = args[-2], args[-1]
            try:
                return await asyncio.wait_for(handler(*args, **kwargs), float(timeout))
            except asyncio.TimeoutError:
                return res.json({"error": "Request timed out"}, status_code=408)
        return wrapper
    return decorator

def capture_request_metadata(log_func):
    """
    A decorator to log request metadata for analysis.

    :param log_func: A function to handle the metadata.
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(*args, **kwargs):
            req, res = args[-2], args[-1]
            metadata = {
                "method": req.method,
                "url": str(req.url),
                "headers": dict(req.headers),
                "client_ip": req.client.host,
            }
            log_func(metadata)
            return await handler(*args, **kwargs)
        return wrapper
    return decorator
def use_for_route(route: str):
    """
    A decorator to apply middleware only to specific routes for both class-based and function-based middleware.
    """
    def decorator(func :Callable):
        @wraps(func)
        async def wrapper_func(request,response, call_next):
            if request.url.path == route:
                return await func(request, response,call_next)
            else:
                return await call_next()
        
        @wraps(func)
        async def wrapper_klass(self,request,response, call_next):
            if request.url.path == route:
                return await func(self,request, response,call_next)
            else:
                return await call_next()
        if func.__name__ == "__call__":
            return wrapper_klass
        else:
            return wrapper_func
        
    return decorator


def use_for_route(route: str):
    if route.endswith("/*"):
        route = route[:-2] 
        route = f"^{route}/.*$"  
    else:
        route = f"^{route}$" 
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper_func(request, response, call_next):
            if re.match(route, request.url.path):
                return await func(request, response, call_next)
            else:
                return await call_next()
        
        @wraps(func)
        async def wrapper_klass(self, request, response, call_next):
            if re.match(route, request.url.path):
                return await func(self, request, response, call_next)
            else:
                return await call_next()

        if func.__name__ == "__call__":
            return wrapper_klass
        else:
            return wrapper_func

    return decorator