
from typing import Any, Callable, List, Union
from .http.request import Request
from .http.response import NexioResponse
from .types import HTTPMethod
from .decorators import allowed_methods
from .routing import Router, Routes,WSRouter
import traceback
from .structs import RouteParam
from .websockets import get_websocket_session
from .middlewares.errors.server_error_handler import ServerErrorMiddleware
import traceback,typing
from .exception_handler import ExceptionMiddleware
from typing_extensions import Doc,Annotated
from nexios.config import MakeConfig
from typing import Awaitable,Sequence
from .types import MiddlewareType ,Scope,Send,Receive
allowed_methods_default = ['get','post','delete','put','patch','options']

from typing import Dict, Any
AppType = typing.TypeVar("AppType", bound="NexioApp")

def validate_params(params: Dict[str, Any], param_types: Dict[str, type]) -> bool:
    errors = []
    for param, expected_type in param_types.items():
        try:
            _param = expected_type(params[param])
        except Exception:
            _param = params[param]
        if param not in params:
            errors.append(f"Missing parameter: {param}")
        
       
        elif not isinstance(_param, expected_type):
            errors.append(f"Parameter '{param}' should be of type {expected_type.__name__}. Got {type(params[param]).__name__}.")
    
    if errors:
        return False, errors
    return True, []


class NexioApp:
    def __init__(self :AppType,
                 config :Annotated[MakeConfig,Doc(
                    """
                    This subclass is derived from the MakeConfig class and is responsible for managing configurations within the Nexios framework. It takes arguments in the form of dictionaries, allowing for structured and flexible configuration handling. By using dictionaries, this subclass makes it easy to pass multiple configuration values at once, reducing complexity and improving maintainability.

                    One of the key advantages of this approach is its ability to dynamically update and modify settings without requiring changes to the core codebase. This is particularly useful in environments where configurations need to be frequently adjusted, such as database settings, API credentials, or feature flags. The subclass can also validate the provided configuration data, ensuring that incorrect or missing values are handled properly.

                    Additionally, this design allows for merging and overriding configurations, making it adaptable for various use cases. Whether used for small projects or large-scale applications, this subclass ensures that configuration management remains efficient and scalable. By extending MakeConfig, it leverages existing functionality while adding new capabilities tailored to Nexios. This makes it an essential component for maintaining structured and well-organized application settings.
                    """
                    
                    
                    )] = None,
    
                    middlewares :Annotated[Sequence[MiddlewareType],Doc(
                        "A list of middlewares, where each middleware is either a class inherited from BaseMiddleware or an asynchronous callable function that accepts request, response, and callnext"
                        )]= [],
                    server_error_handler :Annotated[Awaitable,Doc(
                        """
                        A function in Nexios responsible for handling server-side exceptions by logging errors, reporting issues, or initiating recovery mechanisms. It prevents crashes by intercepting unexpected failures, ensuring the application remains stable and operational. This function provides a structured approach to error management, allowing developers to define custom handling strategies such as retrying failed requests, sending alerts, or gracefully degrading functionality. By centralizing error processing, it improves maintainability and observability, making debugging and monitoring more efficient. Additionally, it ensures that critical failures do not disrupt the entire system, allowing services to continue running while appropriately managing faults and failures.""" )] = None):
        self.config :MakeConfig = config
        self.server_error_handler = None
        self.routes: List[Routes] = []
        self.ws_routes :List[Routes] = []
        self.http_middlewares: List = middlewares or []
        self.ws_middlewares: List =  []
        self.startup_handlers: List[Callable] = []
        self.shutdown_handlers: List[Callable] = []
        self.exceptions_handler = ExceptionMiddleware()

   
    def on_startup(self, handler: Callable[..., Awaitable[Any]]) -> None:
        """
        Registers a startup handler that executes when the application starts.

        This method allows you to define functions that will be executed before
        the application begins handling requests. It is useful for initializing
        resources such as database connections, loading configuration settings, 
        or preparing caches.

        The provided function must be asynchronous (`async def`) since it 
        will be awaited during the startup phase.

        Args:
            handler (Callable): An asynchronous function to be executed at startup.

        Returns:
            Callable: The same handler function, allowing it to be used as a decorator.

        Example:
            ```python

            @app.on_startup
            async def connect_to_db():
                global db
                db = await Database.connect("postgres://user:password@localhost:5432/mydb")
                print("Database connection established.")

            @app.on_startup
            async def cache_warmup():
                global cache
                cache = await load_initial_cache()
                print("Cache warmed up and ready.")
            ```

        In this example:
        - `connect_to_db` establishes a database connection before the app starts.
        - `cache_warmup` preloads data into a cache for faster access.

        These functions will be executed in the order they are registered when the
        application starts.
        """
        self.startup_handlers.append(handler)
        return handler


    def on_shutdown(self, handler: Callable[..., Awaitable[Any]]) -> None:
        """
        Registers a shutdown handler that executes when the application is shutting down.

        This method allows you to define functions that will be executed when the 
        application is stopping. It is useful for cleaning up resources such as 
        closing database connections, saving application state, or gracefully 
        terminating background tasks.

        The provided function must be asynchronous (`async def`) since it will be 
        awaited during the shutdown phase.

        Args:
            handler (Callable): An asynchronous function to be executed during shutdown.

        Returns:
            Callable: The same handler function, allowing it to be used as a decorator.

        Example:
            ```python
            app = NexioApp()

            @app.on_shutdown
            async def disconnect_db():
                global db
                await db.disconnect()
                print("Database connection closed.")

            @app.on_shutdown
            async def clear_cache():
                global cache
                await cache.clear()
                print("Cache cleared before shutdown.")
            ```

        In this example:
        - `disconnect_db` ensures that the database connection is properly closed.
        - `clear_cache` removes cached data to free up memory before the app stops.

        These functions will be executed in the order they are registered when the
        application is shutting down.
        """
        self.shutdown_handlers.append(handler)
        return handler


    async def _startup(self) -> None:
        """Execute all startup handlers sequentially"""
        for handler in self.startup_handlers:
            await handler()

    async def _shutdown(self) -> None:
        """Execute all shutdown handlers sequentially with error handling"""
        for handler in self.shutdown_handlers:
            try:
                await handler()
            except Exception as e:
                self.logger.error(f"Shutdown handler error: {str(e)}")

    async def __handle_lifespan(self, receive: Callable, send: Callable) -> None:
        """Handle ASGI lifespan protocol events"""
        try:
            while True:
                message = await receive()
                
                if message["type"] == "lifespan.startup":
                    try:
                        await self._startup()
                        await send({"type": "lifespan.startup.complete"})
                    except Exception as e:
                        self.logger.error(f"Startup error: {str(e)}")
                        await send({"type": "lifespan.startup.failed", "message": str(e)})
                        return
                
                elif message["type"] == "lifespan.shutdown":
                    try:
                        await self._shutdown()
                        await send({"type": "lifespan.shutdown.complete"})
                        return
                    except Exception as e:
                        self.logger.error(f"Shutdown error: {str(e)}")
                        await send({"type": "lifespan.shutdown.failed", "message": str(e)})
                        return

        except Exception as e:
            self.logger.error(f"Lifespan error: {str(e)}")
            if message["type"].startswith("lifespan.startup"):
                await send({"type": "lifespan.startup.failed", "message": str(e)})
            else:
                await send({"type": "lifespan.shutdown.failed", "message": str(e)})
    def __normalize_path(self,path: str) -> str:
        return path.rstrip("/").lower().replace("//", "/")
   
    
    async def __execute_middleware_stack(self, 
                                     request: Request,
                                     response: NexioResponse, 
                                     handler: Callable = None) -> Any:
        """Execute middleware stack including the handler as the last 'middleware'."""
        async def default_handler(req,res :NexioResponse):
            return res.json({"error":"Not Found"},status_code=404)
        handler = handler or default_handler
        stack = [*self.http_middlewares.copy(),self.exceptions_handler]

        # If we have a handler, add it to the stack
        if handler:
            stack.append(handler)

        index = -1 
        async def next_middleware():
            nonlocal index
            index += 1
            
            if index < len(stack):
                middleware = stack[index]
                if not response._body:
                    if index == len(stack) - 1:  # This is the handler
                        await middleware(request, response)
                    else:
                        await middleware(request, response, next_middleware)
                return

        await next_middleware()

    async def __handle_http_request(self, scope: dict, receive: Callable, send: Callable) -> None:
        request = Request(scope, receive, send)
        response = NexioResponse()
        request.scope['config'] = self.config
       
        
        handler = None
        
        for route in self.routes:
            url = self.__normalize_path(request.url.path)
            match = route.pattern.match(url)
            if match:
                route.handler = allowed_methods(route.methods)(route.handler)
                route_kwargs = match.groupdict()
                handler_validator = getattr(route,"validator",None)
                if handler_validator:
                    is_valid,errors = validate_params(route_kwargs,handler_validator)
                    if not is_valid:
                        response.json({"error":errors},status_code=422)
                        break
                scope['route_params'] = RouteParam(route_kwargs)
                
                
                if route.router_middleware and len(route.router_middleware) > 0:
                    self.http_middlewares.extend(route.router_middleware)
                handler = lambda req, res: route.handler(req, res)
                
                
                break
        await self.__execute_middleware_stack(request, response, handler)
        
        if handler:
            [self.http_middlewares.remove(x) for x in route.router_middleware or []]

     
        
        await response(scope, receive, send)
        return 
    def route(self, path: str, methods: List[Union[str, HTTPMethod]] = allowed_methods_default,validator = None) -> Callable:
        
        """Decorator to register routes with optional HTTP methods"""
        def decorator(handler: Callable) -> Callable:
            handler = allowed_methods(methods)(handler)
            self.add_route(Routes(path, handler,methods=methods,validator=validator))
            return handler
        return decorator
    def ws_route(self, path: str) -> Callable:
        """Decorator to register routes with optional HTTP methods"""
        def decorator(handler: Callable) -> Callable:
            self.add_ws_route(Routes(path, handler))
            return handler
        return decorator
    
    def add_ws_route(self, route: Routes) -> None:
        """Add a route to the application"""
        
        self.ws_routes.append(route)

    def add_route(self, route: Routes) -> None:
        """Add a route to the application"""
        
       
        self.routes.append(route)

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the application"""
        if callable(middleware):
            self.http_middlewares.append(middleware)
        

    def mount_router(self, router: Router) -> None:
        """Mount a router and all its routes to the application"""
        for route in router.get_routes():
            self.add_route(route)

    def mount_ws_router(self, router:WSRouter ) -> None:
        """Mount a router and all its routes to the application"""
        for route in router.get_routes():
            
            self.add_ws_route(route)
    
    async def __execute_ws_middleware_stack(self, ws, **kwargs):
        """
        Executes WebSocket middleware stack after route matching.
        """
        stack = self.ws_middlewares.copy()
        index = -1

        async def next_middleware():
            nonlocal index
            index += 1
            if index < len(stack):
                middleware = stack[index]
                return await middleware(ws, next_middleware, **kwargs)
            else:
                # No more middleware to process
                return None

        return await next_middleware()

    
    async def handler_websocket(self, scope, receive, send):
        ws = await get_websocket_session(scope, receive, send)
        await self.__execute_ws_middleware_stack(ws)
        for route in self.ws_routes:
            url = self.normalize_path(ws.url.path)
            match = route.pattern.match(url)
            
            if match:
                route_kwargs = match.groupdict()
                scope['route_params'] = RouteParam(route_kwargs)
                
                try:
                    await route.execute_middleware_stack(ws)
                    await route.handler(ws, **route_kwargs)
                    return

                except Exception as e:
                    error = traceback.format_exc()
                    self.logger.error(f"WebSocket handler error: {error}")
                    await ws.close(code=1011, reason=f"Internal Server Error: {str(e)}")
                    return

        await ws.close(reason="Not found")
    def add_ws_middleware(self, middleware: Callable) -> None:
        """
        Add a WebSocket middleware to the application.
        """
        if callable(middleware):
            self.ws_middlewares.append(middleware)
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI application callable"""
        if scope["type"] == "lifespan":
            await self.__handle_lifespan(receive, send)
        elif scope["type"] == "http":    
            await self.__handle_http_request(scope, receive, send)

        else:
            await self.handler_websocket(scope, receive, send)

    def get(self, route: Routes,validator = None) -> Callable:
        """Decorator to register a GET route."""
        return self.route(route, methods=["GET"],validator = validator)

    def post(self, route: Routes,validator = None) -> Callable:
        """Decorator to register a POST route."""
        return self.route(route, methods=["POST"],validator= validator)

    def delete(self, route: Routes,validator = None) -> Callable:
        """Decorator to register a DELETE route."""
        return self.route(route, methods=["DELETE"],validator = validator)

    def put(self, route: Routes,validator = None) -> Callable:
        """Decorator to register a PUT route."""
        return self.route(route, methods=["PUT"],validator = validator)

    def patch(self, route: Routes,validator = None) -> Callable:
        """Decorator to register a PATCH route."""
        return self.route(route, methods=["PATCH"],validator = validator)

    def options(self, route: Routes,validator = None) -> Callable:
        """Decorator to register an OPTIONS route."""
        return self.route(route, methods=["OPTIONS"],validator = validator)


    def add_exception_handler(
        self,
        exc_class_or_status_code,
        handler
    ) -> None:
        self.exceptions_handler.add_exception_handler(exc_class_or_status_code,handler)