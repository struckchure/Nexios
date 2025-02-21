from typing import Any, List, Optional, Pattern,Dict,TypeVar,Tuple,Callable,Union
from dataclasses import dataclass
import re
import warnings
from enum import Enum

from nexios.types import MiddlewareType,WsMiddlewareType,HandlerType,WsHandlerType
from nexios.decorators import allowed_methods
from typing_extensions import Doc,Annotated #type: ignore

T = TypeVar("T")
allowed_methods_default = ['get','post','delete','put','patch','options']


class RouteType(Enum):
    REGEX = "regex"
    PATH = "path"
    WILDCARD = "wildcard"

@dataclass
class RoutePattern:
    """Represents a processed route pattern with metadata"""
    pattern: Pattern[str]
    raw_path: str
    param_names: List[str]
    route_type: RouteType

class RouteBuilder:
    """Handles route pattern creation and processing"""
    
    @staticmethod
    def create_pattern(path: str) -> RoutePattern:
        """Create a route pattern from a path string"""
        param_names :List[str] = []
        
        if path.startswith("^"):
            return RoutePattern(
                pattern=re.compile(path),
                raw_path=path,
                param_names=re.findall(r'\?P<(\w+)>', path),
                route_type=RouteType.REGEX
            )
            
        if "*" in path:
            wildcard_pattern = path.replace("*", ".*?")
            return RoutePattern(
                pattern=re.compile(f"^{wildcard_pattern}$"),
                raw_path=path,
                param_names=[],
                route_type=RouteType.WILDCARD
            )
            
        processed_path = path
        

        if path.startswith("^") or path.endswith("$"):
            return RoutePattern(
                pattern=re.compile(path),
                raw_path=path,
                param_names=re.findall(r'\?P<(\w+)>', path),
                route_type=RouteType.REGEX
            )
        
        param_matches = re.finditer(r"{(\w+)(?::([^}]+))?}", path)
        for match in param_matches:
            param_name = match.group(1)
            constraint = match.group(2) or "[^/]+"
            param_names.append(param_name)
            processed_path = processed_path.replace(
                match.group(0),
                f"(?P<{param_name}>{constraint})"
            )
            
        return RoutePattern(
            pattern=re.compile(f"^{processed_path}$"),
            raw_path=path,
            param_names=param_names,
            route_type=RouteType.PATH
        )

class BaseRouter:
    def add_route(self, route: 'Routes') -> None:
        raise NotImplementedError("Not implemented")
    
    def get_routes(self): #type:ignore
        raise NotImplementedError("Not implemented")
    
    def add_middleware(self, middleware: MiddlewareType) -> Any: #type:ignore
        raise NotImplementedError("Not implemented")

class Routes:
    def __init__(
        self,
        path: str,
        handler: Optional[HandlerType],
        methods: Optional[List[str]] = None,
        validator :Optional[Dict[str,type]]= None
    ):
        assert callable(handler), "Route handler must be callable"
        self.validator = validator
        self.raw_path = path
        self.handler = handler
        self.methods = methods or  allowed_methods_default
        self.route_info  = RouteBuilder.create_pattern(path)
        self.pattern :Pattern[str] = self.route_info.pattern
        self.param_names = self.route_info.param_names
        self.route_type = self.route_info.route_type
        self.router_middleware = None
        
   
    
    def match(self, path: str) -> Optional[Dict[str,Any]] :
        """
        Match a path against this route's pattern and return captured parameters
        """
        match = self.pattern.match(path)
        if match:
            return match.groupdict()
        return None
    
    
    def __call__(self) -> Tuple[Pattern[str],HandlerType]:
        """Return the route components for registration"""
        return self.pattern, self.handler
    
    def __repr__(self) -> str:
        return f"<Route {self.raw_path} methods={self.methods}>"
class Router(BaseRouter):
    def __init__(self, prefix: Optional[str] = None, routes :Optional[List[Routes]] = None):
        self.prefix = prefix or ""
        self.routes: List[Routes] =  list(routes) if routes else []
        self.middlewares: List[MiddlewareType] = []
        
        if self.prefix and not self.prefix.startswith("/"):
            warnings.warn("Router prefix should start with '/'")
            self.prefix = f"/{self.prefix}"
    
    def add_route(
        self, 
        route: Annotated[Routes, Doc("An instance of the Routes class representing an HTTP route.")]
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
        _route = Routes(f"{self.prefix}{route.raw_path}",handler=route.handler,methods=route.methods,validator=route.validator)
        self.routes.append(_route)
    
    def add_middleware(self, middleware: MiddlewareType) -> None:
        """Add middleware to the router"""
        if callable(middleware):
            self.middlewares.append(middleware)
    
    def get_routes(self) -> List["Routes"]:
        """Get all routes with their patterns, handlers, and middleware"""
        routes :List[Routes] = []
        for route in self.routes:
            route_ = Routes(
                path=route.raw_path, 
                handler=route.handler, 
                methods=route.methods,
                validator=route.validator)
            setattr(route_,"router_middleware",self.middlewares)
            
            routes.append(route_)
        return routes


    def mount_router(self, router :"Router") -> None:
        """Mount a router and all its routes to the application"""
        self.routes.extend(router.get_routes())

    def get(
        self, 
        route: Annotated[
            str, 
            Doc("The route definition including the path and handler function.")
        ], 
        validator: Annotated[
            Optional[Dict[str,Any]], 
            Doc("An dict to validate request parameters before calling the handler.")
        ] = None
    ) ->Callable[...,Any]:
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
            str, 
            Doc("The route definition including the path and handler function.")
        ], 
        validator: Annotated[
            Optional[Dict[str,Any]], 
            Doc("An dict to validate request parameters before calling the handler.")
        ] = None
    ) ->  Callable[...,Any]:
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
            str, 
            Doc("The route definition including the path and handler function.")
        ], 
        validator: Annotated[
            Optional[Dict[str,Any]], 
            Doc("An dict to validate request parameters before calling the handler.")
        ] = None
    ) ->  Callable[...,Any]:
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
            str, 
            Doc("The route definition including the path and handler function.")
        ], 
        validator: Annotated[
            Optional[Dict[str,Any]], 
            Doc("An dict to validate request parameters before calling the handler.")
        ] = None
    ) ->  Callable[...,Any]:
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
            str, 
            Doc("The route definition including the path and handler function.")
        ], 
        validator: Annotated[
            Optional[Dict[str,Any]], 
            Doc("An dict to validate request parameters before calling the handler.")
        ] = None
    ) -> Callable[...,Any]:
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
            str, 
            Doc("The route definition including the path and handler function.")
        ], 
        validator: Annotated[
            Optional[Dict[str,Any]], 
            Doc("An dict to validate request parameters before calling the handler.")
        ] = None
    ) ->  Callable[...,Any]:
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



   
            
    
    def route(
        self,
        path: Annotated[str, Doc("The URL pattern for the route. Must be a valid string path.")], 
        methods: Annotated[
            List[str], 
            Doc("A list of allowed HTTP methods (e.g., ['GET', 'POST']). Defaults to all methods.")
        ] = allowed_methods_default,
        validator: Annotated[
            Optional[Dict[str,Any]], 
            Doc("An dict to validate request parameters before calling the handler.")
        ] = None
    ) -> Callable[...,Any]:
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
        def decorator(handler: HandlerType) -> HandlerType: #type: ignore
            _handler:HandlerType = allowed_methods(methods)(handler)  
            route = Routes(f"{path}", _handler, methods=methods, validator=validator)
            self.add_route(route)
            return _handler  
        return decorator  
    
    def __repr__(self) -> str:
        return f"<Router prefix='{self.prefix}' routes={len(self.routes)}>"



    

class WebsocketRoutes:
    def __init__(
        self,
        path: str,
        handler: WsHandlerType,
        middleware: Optional[WsMiddlewareType] = None
    ):
        assert callable(handler), "Route handler must be callable"
        self.raw_path = path
        self.handler:WsHandlerType = handler
        self.middleware  = middleware
        self.route_info = RouteBuilder.create_pattern(path)
        self.pattern = self.route_info.pattern
        self.param_names = self.route_info.param_names
        self.route_type = self.route_info.route_type
        self.router_middleware = None
    
    def match(self, path: str) -> Optional[Dict[str,Any]]:
        """
        Match a path against this route's pattern and return captured parameters
        """
        match = self.pattern.match(path)
        if match:
            return match.groupdict()
        return None
    
    
    def __call__(self) -> Tuple[Pattern[str],WsHandlerType,Union[WsMiddlewareType,None] ]:
        """Return the route components for registration"""
        return self.pattern, self.handler, self.middleware
    
    def __repr__(self) -> str:
        return f"<WSRoute {self.raw_path}>"
    
    async def execute_middleware_stack(self, ws :"WebsocketRoutes", **kwargs :Dict[str,Any]) -> Union[WsMiddlewareType , None]:
        """
        Executes WebSocket middleware stack after route matching.
        """
        middleware_list :List[WsMiddlewareType] = getattr(self,"router_middleware") or [] #type: ignore

        stack :List[WsMiddlewareType] = middleware_list.copy() 
        index = -1

        async def next_middleware() -> WsMiddlewareType:
            nonlocal index
            index += 1
            if index < len(stack): #type: ignore
                middleware:List[MiddlewareType] = stack[index] #type: ignore
                return await middleware(ws, next_middleware, **kwargs)#type: ignore
            else:
                # No more middleware to process
                return None #type: ignore

        return await next_middleware()
    


class WSRouter(BaseRouter):
    def __init__(self, prefix: Optional[str] = None):
        self.prefix = prefix or ""
        self.routes: List[WebsocketRoutes] = []
        self.middlewares: List[WsMiddlewareType] = []
        
        if self.prefix and not self.prefix.startswith("/"):
            warnings.warn("WSRouter prefix should start with '/'")
            self.prefix = f"/{self.prefix}"
    
    def add_ws_route(
        self, 
        route: Annotated[WebsocketRoutes, Doc("An instance of the Routes class representing a WebSocket route.")]
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
        self.routes.append(route)
    
    def add_middleware(self, middleware: WsMiddlewareType) -> None: #type: ignore[override]
        """Add middleware to the WebSocket router"""
        if callable(middleware):
            self.middlewares.append(middleware)
    
    def get_routes(self) -> List[WebsocketRoutes]:
        """Get all WebSocket routes with their patterns, handlers, and middleware"""
        routes :List[WebsocketRoutes]= []
        for route in self.routes:
            route_ = WebsocketRoutes(
                path=route.raw_path, 
                handler=route.handler, 
                middleware=route.middleware
            )
            setattr(route_, "router_middleware", self.middlewares)
            routes.append(route_)
        return routes

    def ws_route(
        self, 
        path: Annotated[str, Doc("The WebSocket route path. Must be a valid URL pattern.")]
    ) -> Union[WsHandlerType , Any]:
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
    
    

    

    def __repr__(self) -> str:
        return f"<WSRouter prefix='{self.prefix}' routes={len(self.routes)}>"