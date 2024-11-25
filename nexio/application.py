from typing import Any, Callable, AsyncIterator, List, Union
from .http.request import Request
from .http.response import NexioResponse
from starlette.responses import JSONResponse
from .types import HTTPMethod
from .decorators import AllowedMethods
from .routers import Router, Routes
from enum import Enum
from .config.settings import BaseConfig
import logging
from contextlib import asynccontextmanager


class NexioApp:
    def __init__(self, 
                 config: Enum = BaseConfig,
                 middlewares :list = [],
                 ):
        self.config = config
        self.routes: List[str] = []
        self.middlewares: List = middlewares
        self.startup_handlers: List[Callable] = []
        self.shutdown_handlers: List[Callable] = []
        self.logger = logging.getLogger("nexio")
        self._db_initialized = False
        

    def on_startup(self, handler: Callable) -> Callable:
        """
        Decorator to register startup handlers
        """
        self.startup_handlers.append(handler)
        return handler

    def on_shutdown(self, handler: Callable) -> Callable:
        """
        Decorator to register shutdown handlers
        """
        self.shutdown_handlers.append(handler)
        return handler

    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[None]:
        """
        Application context manager that handles startup and shutdown events
        by executing all registered handlers in sequence.
        """
        try:
            self.logger.info("Application startup initiated")
            for handler in self.startup_handlers:
                await handler()
            self.logger.info("Application startup completed")
            yield
        finally:
            self.logger.info("Application shutdown initiated")
            for handler in self.shutdown_handlers:
                try:
                    await handler()
                except Exception as e:
                   
                    pass
            self.logger.info("Application shutdown completed")

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

    async def handle_request(self, scope: dict, receive: Callable, send: Callable) -> None:
        request = Request(scope, receive, send)
        response = NexioResponse()
        request.scope['config'] = self.config

        for path_pattern, handler, middleware in self.routes:
            match = path_pattern.match(request.url.path)
            if match:
                kwargs = match.groupdict()
                request.url_params = kwargs
                
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

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    try:
                        async with self.lifespan():
                            await send({"type": "lifespan.startup.complete"})
                            # Wait for shutdown message
                            while True:
                                message = await receive()
                                # Handling RuntimeError because our event loop sometimes decides to clock out early.
                                # Skipping over it for now, but we should revisit and see if it just needs a coffee break.
                                # TODO: Dig deeper and give our event loop some TLC.

                                if message["type"] == "lifespan.shutdown":
                                    await send({"type": "lifespan.shutdown.complete"})
                                    break
                            return
                    except Exception as e:
                        self.logger.error(f"Lifespan error: {str(e)}")
                        await send({"type": "lifespan.startup.failed", "message": str(e)})
                    return
        elif scope["type"] == "http":    
            await self.handle_request(scope, receive, send)