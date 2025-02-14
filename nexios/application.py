from typing import Any, Callable, List, Union
from .http.request import Request
from .http.response import NexioResponse
from .types import HTTPMethod
from .decorators import allowed_methods
from .routing import Router, Routes, WSRouter, WebsocketRoutes
from .structs import RouteParam
from .websockets import get_websocket_session, WebSocket
import traceback, typing
from .exception_handler import ExceptionMiddleware
from typing_extensions import Doc, Annotated  # type:ignore
from nexios.config import MakeConfig
from typing import Awaitable, Optional
from .types import (
    MiddlewareType,
    Scope,
    Send,
    Receive,
    WsMiddlewareType,
    Message,
    HandlerType,
    WsHandlerType,
)

allowed_methods_default = ["get", "post", "delete", "put", "patch", "options"]

from typing import Dict, Any

AppType = typing.TypeVar("AppType", bound="NexiosApp")


def validate_params(
    params: Dict[str, Any], param_types: Dict[str, type]
) -> typing.Tuple[bool, List[str]]:
    errors: List[str] = []
    for param, expected_type in param_types.items():
        try:
            _param = expected_type(params[param])
        except Exception as _:
            raise ValueError(
                "Cannot validate path parameters for a route that has none."
            )

        if param not in params:
            errors.append(f"Missing parameter: {param}")

        elif not isinstance(_param, expected_type):
            errors.append(
                f"Parameter '{param}' should be of type {expected_type.__name__}. Got {type(params[param]).__name__}."
            )

    if errors:
        return False, errors
    return True, []


class NexiosApp:
    def __init__(
        self,
        config: Annotated[
            Optional[MakeConfig],
            Doc(
                """
                    This subclass is derived from the MakeConfig class and is responsible for managing configurations within the Nexios framework. It takes arguments in the form of dictionaries, allowing for structured and flexible configuration handling. By using dictionaries, this subclass makes it easy to pass multiple configuration values at once, reducing complexity and improving maintainability.

                    One of the key advantages of this approach is its ability to dynamically update and modify settings without requiring changes to the core codebase. This is particularly useful in environments where configurations need to be frequently adjusted, such as database settings, API credentials, or feature flags. The subclass can also validate the provided configuration data, ensuring that incorrect or missing values are handled properly.

                    Additionally, this design allows for merging and overriding configurations, making it adaptable for various use cases. Whether used for small projects or large-scale applications, this subclass ensures that configuration management remains efficient and scalable. By extending MakeConfig, it leverages existing functionality while adding new capabilities tailored to Nexios. This makes it an essential component for maintaining structured and well-organized application settings.
                    """
            ),
        ] = None,
        middlewares: Annotated[
            List[MiddlewareType],
            Doc(
                "A list of middlewares, where each middleware is either a class inherited from BaseMiddleware or an asynchronous callable function that accepts request, response, and callnext"
            ),
        ] = [],
        server_error_handler: Annotated[
            Optional[Awaitable[NexioResponse]],
            Doc(
                """
                        A function in Nexios responsible for handling server-side exceptions by logging errors, reporting issues, or initiating recovery mechanisms. It prevents crashes by intercepting unexpected failures, ensuring the application remains stable and operational. This function provides a structured approach to error management, allowing developers to define custom handling strategies such as retrying failed requests, sending alerts, or gracefully degrading functionality. By centralizing error processing, it improves maintainability and observability, making debugging and monitoring more efficient. Additionally, it ensures that critical failures do not disrupt the entire system, allowing services to continue running while appropriately managing faults and failures."""
            ),
        ] = None,
    ):
        self.config = config
        self.server_error_handler = None
        self.routes: List[Routes] = []
        self.ws_routes: List[WebsocketRoutes] = []
        self.http_middlewares: List[MiddlewareType] = middlewares or []
        self.ws_middlewares: List[WsMiddlewareType] = []
        self.startup_handlers: List[Callable[[], Awaitable[None]]] = []
        self.shutdown_handlers: List[Callable[[], Awaitable[None]]] = []
        self.exceptions_handler: Any[ExceptionMiddleware, None] = (
            server_error_handler or ExceptionMiddleware()
        )

    def on_startup(self, handler: Callable[[], Awaitable[None]]) -> None:
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

    def on_shutdown(self, handler: Callable[[], Awaitable[None]]) -> None:
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

    async def _startup(self) -> None:
        """Execute all startup handlers sequentially"""
        for handler in self.startup_handlers:
            try:
                await handler()
            except Exception as e:
                raise e

    async def _shutdown(self) -> None:
        """Execute all shutdown handlers sequentially with error handling"""
        for handler in self.shutdown_handlers:
            try:
                await handler()
            except Exception as e:
                raise e

    async def __handle_lifespan(self, receive: Receive, send: Send) -> None:
        """Handle ASGI lifespan protocol events"""
        try:
            while True:
                message: Message = await receive()

                if message["type"] == "lifespan.startup":
                    try:
                        await self._startup()
                        await send({"type": "lifespan.startup.complete"})
                    except Exception as e:
                        await send(
                            {"type": "lifespan.startup.failed", "message": str(e)}
                        )
                        return

                elif message["type"] == "lifespan.shutdown":
                    try:
                        await self._shutdown()
                        await send({"type": "lifespan.shutdown.complete"})
                        return
                    except Exception as e:
                        await send(
                            {"type": "lifespan.shutdown.failed", "message": str(e)}
                        )
                        return

        except Exception as e:
            if message["type"].startswith("lifespan.startup"):  # type: ignore
                await send({"type": "lifespan.startup.failed", "message": str(e)})
            else:
                await send({"type": "lifespan.shutdown.failed", "message": str(e)})

    def __normalize_path(self, path: str) -> str:
        return path.rstrip("/").lower().replace("//", "/")

    async def __execute_middleware_stack(
        self,
        request: Request,
        response: NexioResponse,
        handler: Optional[HandlerType] = None,# type: ignore
    ) -> Any:
        """Execute middleware stack including the handler as the last 'middleware'."""

        async def default_handler(req: Request, res: NexioResponse):
            return res.json({"error": "Not Found"}, status_code=404)

        handler: Optional[HandlerType] | None = handler or default_handler  # type: ignore
        stack: List[MiddlewareType] = [
            *self.http_middlewares.copy(),
            self.exceptions_handler,
        ]  # type: ignore

        if handler:  # type:ignore
            stack.append(handler)  # type:ignore

        index = -1

        async def next_middleware():
            nonlocal index
            index += 1

            if index < len(stack):
                middleware = stack[index]

                if index == len(stack) - 1:
                    await middleware(request, response)  # type:ignore
                else:
                    await middleware(request, response, next_middleware)
                return

        await next_middleware()

    async def __handle_http_request(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        request = Request(scope, receive, send)
        response = NexioResponse()
        request.scope["config"] = self.config

        handler = None

        for route in self.routes:
            url = self.__normalize_path(request.url.path)
            match = route.pattern.match(url)
            if match:
                route.handler = allowed_methods(route.methods)(route.handler)
                route_kwargs = match.groupdict()
                handler_validator = getattr(route, "validator", None)
                if handler_validator:
                    is_valid, errors = validate_params(route_kwargs, handler_validator)
                    if not is_valid:
                        response.json({"error": errors}, status_code=422)
                        break
                scope["route_params"] = RouteParam(route_kwargs)

                if route.router_middleware and len(route.router_middleware) > 0:
                    self.http_middlewares.extend(route.router_middleware)
                handler = lambda req, res: route.handler(req, res)  # type: ignore

                break
        await self.__execute_middleware_stack(request, response, handler)  # type: ignore

        if handler:
            [self.http_middlewares.remove(x) for x in route.router_middleware or []]  # type: ignore

        await response(scope, receive, send)
        return

    def route(
        self,
        path: Annotated[
            str, Doc("The URL pattern for the route. Must be a valid string path.")
        ],
        methods: Annotated[
            List[Union[str, HTTPMethod]],
            Doc(
                "A list of allowed HTTP methods (e.g., ['GET', 'POST']). Defaults to all methods."
            ),
        ] = allowed_methods_default,
        validator: Annotated[
            Optional[Dict[str, Any]],
            Doc("An dict to validate request parameters before calling the handler."),
        ] = None,
    ) -> Callable[..., Any]:
        """
        Registers a route with the specified HTTP methods and an optional validator.

        This decorator allows developers to define HTTP routes for the application by specifying
        the URL path, allowed methods, and an optional parameter validator. It ensures that the
        handler only responds to the defined HTTP methods.



        Example:
            ```python

            @app.route("/users", methods=["GET"])
            async def get_users(request, response):
                response.json({"users": ["Alice", "Bob"]})

            @app.route("/users", methods=["POST"])
            async def create_user(request, response):
                response.json({"message": "User created"}, status_code=201)
            ```
        """

        def decorator(handler: HandlerType) -> HandlerType:  # type: ignore
            _handler: HandlerType = allowed_methods(methods)(
                handler
            )  # type :ignore[no-reder]
            self.add_route(Routes(path, _handler, methods=methods, validator=validator))
            return _handler

        return decorator

    def ws_route(
        self,
        path: Annotated[
            str, Doc("The WebSocket route path. Must be a valid URL pattern.")
        ],
    ) -> Callable[..., WsHandlerType]:
        """
        Registers a WebSocket route.

        This decorator is used to define WebSocket routes in the application, allowing handlers
        to manage WebSocket connections. When a WebSocket client connects to the given path,
        the specified handler function will be executed.

        Returns:
            Callable: The original WebSocket handler function.

        Example:
            ```python

            @app.ws_route("/ws/chat")
            async def chat_handler(websocket):
                await websocket.accept()
                while True:
                    message = await websocket.receive_text()
                    await websocket.send_text(f"Echo: {message}")
            ```
        """

        def decorator(handler: WsHandlerType) -> WsHandlerType:
            self.add_ws_route(WebsocketRoutes(path, handler))
            return handler

        return decorator

    def add_ws_route(
        self,
        route: Annotated[
            WebsocketRoutes,
            Doc("An instance of the Routes class representing a WebSocket route."),
        ],
    ) -> None:
        """
        Adds a WebSocket route to the application.

        This method registers a WebSocket route, allowing the application to handle WebSocket connections.

        Args:
            route (Routes): The WebSocket route configuration.

        Returns:
            None

        Example:
            ```python
            route = Routes("/ws/chat", chat_handler)
            app.add_ws_route(route)
            ```
        """
        self.ws_routes.append(route)

    def add_route(
        self,
        route: Annotated[
            Routes, Doc("An instance of the Routes class representing an HTTP route.")
        ],
    ) -> None:
        """
        Adds an HTTP route to the application.

        This method registers an HTTP route, allowing the application to handle requests for a specific URL path.

        Args:
            route (Routes): The HTTP route configuration.

        Returns:
            None

        Example:
            ```python
            route = Routes("/home", home_handler, methods=["GET", "POST"])
            app.add_route(route)
            ```
        """
        self.routes.append(route)

    def add_middleware(
        self,
        middleware: Annotated[
            MiddlewareType,
            Doc(
                "A callable middleware function that processes requests and responses."
            ),
        ],
    ) -> None:
        """
        Adds middleware to the application.

        Middleware functions are executed in the request-response lifecycle, allowing
        modifications to requests before they reach the route handler and responses
        before they are sent back to the client.

        Args:
            middleware (MiddlewareType): A callable that takes a `Request`, `Response`,
            and a `Callable` (next middleware or handler) and returns a `Response`.

        Returns:
            None

        Example:
            ```python
            def logging_middleware(request: Request, response: Response, next_call: Callable) -> Response:
                print(f"Request received: {request.method} {request.url}")
                return next_call(request, response)

            app.add_middleware(logging_middleware)
            ```
        """
        if callable(middleware):
            self.http_middlewares.append(middleware)

    def mount_router(
        self,
        router: Annotated[
            Router,
            Doc("An instance of Router containing multiple routes to be mounted."),
        ],
    ) -> None:
        """
        Mounts a router and all its routes to the application.

        This method allows integrating another `Router` instance, registering all its
        defined routes into the current application. It is useful for modularizing routes
        and organizing large applications.

        Args:
            router (Router): The `Router` instance whose routes will be added.

        Returns:
            None

        Example:
            ```python
            user_router = Router()

            @user_router.route("/users", methods=["GET"])
            def get_users(request, response):
                 response.json({"users": ["Alice", "Bob"]})

            app.mount_router(user_router)  # Mounts the user routes into the main app
            ```
        """
        for route in router.get_routes():
            self.add_route(route)

    def mount_ws_router(
        self,
        router: Annotated[
            "WSRouter",
            Doc("An instance of Router containing multiple routes to be mounted."),
        ],
    ) -> None:
        """
        Mounts a router and all its routes to the application.

        This method allows integrating another `Router` instance, registering all its
        defined routes into the current application. It is useful for modularizing routes
        and organizing large applications.

        Args:
            router (Router): The `Router` instance whose routes will be added.

        Returns:
            None

        Example:
            ```python
            chat_router = WSRouter()

            @chat_router.ws("/users")
            def get_users(ws):
                ...

            app.mount_ws_router(chat_router)  # Mounts the user routes into the main app
            ```
        """
        for route in router.get_routes():
            self.add_ws_route(route)

    async def __execute_ws_middleware_stack(
        self, ws: WebSocket, **kwargs: Dict[str, Any]
    ) -> None:
        """
        Executes WebSocket middleware stack after route matching.
        """
        stack = self.ws_middlewares.copy()
        index = -1

        async def next_middleware() -> None:
            nonlocal index
            index += 1
            if index < len(stack):
                middleware = stack[index]
                return await middleware(ws, next_middleware, **kwargs)  # type:ignore
            else:
                return None

        return await next_middleware()

    async def __handle_websocket(self, scope: Scope, receive: Receive, send: Send):
        ws = await get_websocket_session(scope, receive, send)
        await self.__execute_ws_middleware_stack(ws)
        for route in self.ws_routes:
            url = self.__normalize_path(ws.url.path)
            match = route.pattern.match(url)

            if match:
                route_kwargs = match.groupdict()
                scope["route_params"] = RouteParam(route_kwargs)

                try:
                    await route.execute_middleware_stack(ws)  # type: ignore
                    await route.handler(ws, **route_kwargs)
                    return

                except Exception as _:
                    error = traceback.format_exc()
                    await ws.close(
                        code=1011, reason=f"Internal Server Error: {str(error)}"
                    )
                    return

        await ws.close(reason="Not found")
        return

    def add_ws_middleware(
        self,
        middleware: Annotated[
            WsMiddlewareType,
            Doc(
                "A callable function that intercepts and processes WebSocket connections."
            ),
        ],
    ) -> None:
        """
        Adds a WebSocket middleware to the application.

        WebSocket middleware functions allow pre-processing of WebSocket requests before they
        reach their final handler. Middleware can be used for authentication, logging, or
        modifying the WebSocket request/response.

        Args:
            middleware (Callable): A callable function that handles WebSocket connections.

        Returns:
            None

        Example:
            ```python
            def ws_auth_middleware(ws, next_handler):
                if not ws.headers.get("Authorization"):
                    ...
                return next_handler(ws)

            app.add_ws_middleware(ws_auth_middleware)
            ```
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
            await self.__handle_websocket(scope, receive, send)

    def get(
        self,
        route: Annotated[
            str, Doc("The route definition including the path and handler function.")
        ],
        validator: Annotated[
            Optional[Dict[str, Any]],
            Doc("An dict to validate request parameters before calling the handler."),
        ] = None,
    ) -> Callable[..., Any]:
        """
        Registers a GET route.

        This decorator allows you to define an endpoint that handles HTTP GET requests.
        GET requests are typically used for retrieving resources.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.get("/users")
            async def get_users(request,response):
                return response.json({"users": ["Alice", "Bob"]})
            ```
        """
        return self.route(route, methods=["GET"], validator=validator)

    def post(
        self,
        route: Annotated[
            str, Doc("The route definition including the path and handler function.")
        ],
        validator: Annotated[
            Optional[Dict[str, Any]],
            Doc("An dict to validate request parameters before calling the handler."),
        ] = None,
    ) -> Callable[..., Any]:
        """
        Registers a POST route.

        This decorator is used to define an endpoint that handles HTTP POST requests,
        typically for creating resources.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.post("/users")
            async def create_user(request,response):
                return response.json({"message": "User created"})
            ```
        """
        return self.route(route, methods=["POST"], validator=validator)

    def delete(
        self,
        route: Annotated[
            str, Doc("The route definition including the path and handler function.")
        ],
        validator: Annotated[
            Optional[Dict[str, Any]],
            Doc("An dict to validate request parameters before calling the handler."),
        ] = None,
    ) -> Callable[..., Any]:
        """
        Registers a DELETE route.

        This decorator allows defining an endpoint that handles HTTP DELETE requests,
        typically for deleting resources.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.delete("/users/{user_id}")
            def delete_user(request, response):
                user_id = request.path_params.user_id
                return responsejson({"message": f"User {user_id} deleted"})
            ```
        """
        return self.route(route, methods=["DELETE"], validator=validator)

    def put(
        self,
        route: Annotated[
            str, Doc("The route definition including the path and handler function.")
        ],
        validator: Annotated[
            Optional[Dict[str, Any]],
            Doc("An dict to validate request parameters before calling the handler."),
        ] = None,
    ) -> Callable[..., Any]:
        """
        Registers a PUT route.

        This decorator defines an endpoint that handles HTTP PUT requests,
        typically for updating or replacing a resource.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.delete("/users/{user_id}")
            def delete_user(request, response):
                user_id = request.path_params.user_id
                return responsejson({"message": f"User {user_id} updated"})
        """
        return self.route(route, methods=["PUT"], validator=validator)

    def patch(
        self,
        route: Annotated[
            str, Doc("The route definition including the path and handler function.")
        ],
        validator: Annotated[
            Optional[Dict[str, Any]],
            Doc("An dict to validate request parameters before calling the handler."),
        ] = None,
    ) -> Callable[..., Any]:
        """
        Registers a PATCH route.

        This decorator defines an endpoint that handles HTTP PATCH requests,
        which are used to apply partial modifications to a resource.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.patch("/users/{user_id}")
            def partial_update_user(request, response):
                user_id = request.path_params.user_id

                return respoonse.json({"message": f"User {user_id} partially updated"})
            ```
        """
        return self.route(route, methods=["PATCH"], validator=validator)

    def options(
        self,
        route: Annotated[
            str, Doc("The route definition including the path and handler function.")
        ],
        validator: Annotated[
            Optional[Dict[str, Any]],
            Doc("An dict to validate request parameters before calling the handler."),
        ] = None,
    ) -> Callable[..., Any]:
        """
        Registers an OPTIONS route.

        This decorator defines an endpoint that handles HTTP OPTIONS requests,
        which are used to describe the communication options for the target resource.
        OPTIONS requests are commonly used in CORS (Cross-Origin Resource Sharing)
        to check allowed methods, headers, and authentication rules.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.options("/users")
            def options_users(request):
                return response.json({
                    "Allow": "GET, POST, DELETE, OPTIONS"
                })
            ```
        """
        return self.route(route, methods=["OPTIONS"], validator=validator)

    def add_exception_handler(
        self,
        exc_class_or_status_code: Union[typing.Type[Exception], int],
        handler: HandlerType,
    ) -> None:
        self.exceptions_handler.add_exception_handler(exc_class_or_status_code, handler)
        
        
        
