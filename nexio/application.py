from typing import Any, Awaitable, Callable, Mapping, Sequence, List, Union, Optional
from .http.request import Request
from .http.response import NexioResponse
from starlette.responses import JSONResponse
import re
from .types import HTTPMethod
from .decorators import AllowedMethods
from .routers import Router, Routes
from enum import Enum
from .config.settings import BaseConfig
from .files import LocalFileStorage
import logging
from contextlib import asynccontextmanager

class NexioHTTPApp:
    def __init__(self, config: Enum = BaseConfig):
        self.config = config
        self.routes: List[str] = []
        self.middlewares: List = []
        self.start_function: Optional[Callable] = None
        self.shutdown_function: Optional[Callable] = None
        self.logger = logging.getLogger("nexio")
        
    def on_start(self, func: Callable) -> Callable:
        """Register startup handler"""
        self.start_function = func
        return func
    
    def on_shutdown(self, func: Callable) -> Callable:
        """Register shutdown handler"""
        self.shutdown_function = func
        return func

    async def startup(self) -> None:
        """Execute startup tasks"""
        if callable(self.start_function):
            try:
                await self.start_function()
                self.logger.info("Application startup complete")
            except Exception as e:
                self.logger.error(f"Startup failed: {str(e)}")
                raise

    async def shutdown(self) -> None:
        """Execute shutdown tasks"""
        print("shutting down !!!")
        if callable(self.shutdown_function):
            try:
                await self.shutdown_function()
                self.logger.info("Application shutdown complete")
            except Exception as e:
                self.logger.error(f"Shutdown failed: {str(e)}")
                raise

    async def execute_middleware_stack(self, 
                                     request: Request,
                                     response: NexioResponse, 
                                     middleware: Callable, 
                                     handler: Callable, 
                                     **kwargs) -> Any:
        stack = self.middlewares
        if callable(middleware):
            stack.append(middleware)
        index = -1 
        
        async def next_middleware():
            nonlocal index
            index += 1
            
            if index < len(stack):
                middleware = stack[index]
                return await middleware(request, response, next_middleware, **kwargs)
            else:
                return await handler(request, response, **kwargs)
            
        return await next_middleware()
    @asynccontextmanager
    async def lifespan_context(self,func :Callable):
        """Handle lifespan events with a context manager for resources."""
        if callable(func):
            try:
                await func()
                self.logger.info("Application startup complete")
            except Exception as e:
                self.logger.error(f"Startup failed: {str(e)}")
                raise

        try:
            yield
        finally:
            pass

    async def handle_request(self, scope: dict, receive: Callable, send: Callable) -> None:
        request = Request(scope, receive, send)
        response = NexioResponse()

        for path_pattern, handler, middleware in self.routes:
            match = path_pattern.match(request.url.path)
            if match:
                kwargs = match.groupdict()
                request.url_params = kwargs
                request.app_config = self.config
                try:
                    await self.execute_middleware_stack(request,
                                                      response,
                                                      middleware,
                                                      handler)
                except Exception as e:
                    self.logger.error(f"Request handler error: {str(e)}")
                    error_response = JSONResponse(
                        {"error": str(e)},
                        status_code=500
                    )
                    await error_response(scope, receive, send)
                await response(scope, receive, send)
                return

        error_response = JSONResponse({"error": "Not found"}, status_code=404)
        await error_response(scope, receive, send)

    def route(self, path: str, methods: List[Union[str, HTTPMethod]] = None) -> Callable:
        def decorator(handler: Callable) -> Callable:
            middlewares = []
            if methods:
                middlewares.append(AllowedMethods(methods))
            self.add_route(path, handler, middlewares)
            return handler
        return decorator

    def add_route(self, route: Routes) -> None:
        route, handler, middleware = route()
        self.routes.append((route, handler, middleware))

    def add_middleware(self, middleware: Callable) -> None:
        if callable(middleware):
            self.middlewares.append(middleware)

    def mount_router(self, router: Router) -> None:
        for route in router.get_routes():
            self.add_route(route)

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> Any:
        
        if scope["type"] == "lifespan":
            message = await receive()
            print(message)
            if message["type"] == "lifespan.startup":
                print("scope type is",message['type'])
                await self.startup()
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                

                await self.shutdown()
                await send({"type": "lifespan.shutdown.complete"})
            else:
                await self.shutdown()
        elif scope["type"] == "http":    
            await self.handle_request(scope, receive, send)

        