from typing import Any, List, Callable, Union, Optional, Pattern
from dataclasses import dataclass
import re
import warnings
from enum import Enum
from nexios.http.response import NexioResponse
from nexios.http.request import Request
allowed_methods = ['get','post','put','delete','patch','delete','options']
class RouteType(Enum):
    REGEX = "regex"
    PATH = "path"
    WILDCARD = "wildcard"

@dataclass
class RoutePattern:
    """Represents a processed route pattern with metadata"""
    pattern: Pattern
    raw_path: str
    param_names: List[str]
    route_type: RouteType

class RouteBuilder:
    """Handles route pattern creation and processing"""
    
    @staticmethod
    def create_pattern(path: str) -> RoutePattern:
        """Create a route pattern from a path string"""
        param_names = []
        
        # Handle regex routes that start with ^
        if path.startswith("^"):
            return RoutePattern(
                pattern=re.compile(path),
                raw_path=path,
                param_names=re.findall(r'\?P<(\w+)>', path),
                route_type=RouteType.REGEX
            )
            
        # Handle wildcard routes
        if "*" in path:
            wildcard_pattern = path.replace("*", ".*?")
            return RoutePattern(
                pattern=re.compile(f"^{wildcard_pattern}$"),
                raw_path=path,
                param_names=[],
                route_type=RouteType.WILDCARD
            )
            
        # Process path parameters
        processed_path = path
        

        # If the path starts with ^ or ends with $, treat it as a regex
        if path.startswith("^") or path.endswith("$"):
            return RoutePattern(
                pattern=re.compile(path),
                raw_path=path,
                param_names=re.findall(r'\?P<(\w+)>', path),
                route_type=RouteType.REGEX
            )
        
        # Handle URL parameters like {param}
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
    
    def get_routes(self) -> List[tuple]:
        raise NotImplementedError("Not implemented")
    
    def add_middleware(self, middleware: Callable) -> None:
        raise NotImplementedError("Not implemented")

class Router(BaseRouter):
    def __init__(self, prefix: Optional[str] = None):
        self.prefix = prefix or ""
        self.routes: List[Routes] = []
        self.middlewares: List[Callable] = []
        
        if self.prefix and not self.prefix.startswith("/"):
            warnings.warn("Router prefix should start with '/'")
            self.prefix = f"/{self.prefix}"
    
    def add_route(self, route: 'Routes') -> None:
        """Add a route with proper prefix handling"""
        if self.prefix:
            # Create new route with prefixed path
            prefixed_route = Routes(
                f"{self.prefix}{route.raw_path}",
                route.handler,
                methods=route.methods
            )
            self.routes.append(prefixed_route)
        else:
            self.routes.append(route)
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the router"""
        if callable(middleware):
            self.middlewares.append(middleware)
    
    def get_routes(self) -> List[tuple]:
        """Get all routes with their patterns, handlers, and middleware"""
        routes = []
        for route in self.routes:
            route_ = Routes(
                path=route.raw_path, 
                handler=route.handler, 
                methods=route.methods)
            setattr(route_,"router_middleware",self.middlewares)
            
            routes.append(route_)
        return routes

    def handle(self):pass
    def get(self, path: str) -> Callable:
        """Decorator to register a GET route."""
        return self.route(path, methods=["GET"])

    def post(self, path: str) -> Callable:
        """Decorator to register a POST route."""
        return self.route(path, methods=["POST"])

    def delete(self, path: str) -> Callable:
        """Decorator to register a DELETE route."""
        return self.route(path, methods=["DELETE"])

    def put(self, path: str) -> Callable:
        """Decorator to register a PUT route."""
        return self.route(path, methods=["PUT"])

    def patch(self, path: str) -> Callable:
        """Decorator to register a PATCH route."""
        return self.route(path, methods=["PATCH"])

    def options(self, path: str) -> Callable:
        """Decorator to register an OPTIONS route."""
        return self.route(path, methods=["OPTIONS"])

            
    
    def route(self, path: str, methods: Optional[List[str]] = None) -> Callable:
        """Route decorator with method restrictions"""
        def decorator(handler: Callable) -> Callable:
            route = Routes(path, handler, methods=methods)
            self.add_route(route)
            return handler
        return decorator
    
    def __repr__(self) -> str:
        return f"<Router prefix='{self.prefix}' routes={len(self.routes)}>"


class Routes:
    def __init__(
        self,
        path: str,
        handler: Callable,
        methods: Optional[List[str]] = None
    ):
        
        assert callable(handler), "Route handler must be callable"
        self.raw_path = path
        self.handler = handler
        self.methods = methods or  allowed_methods
        route_info = RouteBuilder.create_pattern(path)
        self.pattern = route_info.pattern
        self.param_names = route_info.param_names
        self.route_type = route_info.route_type
        self.router_middleware = None
    
    def match(self, path: str) -> Optional[dict]:
        """
        Match a path against this route's pattern and return captured parameters
        """
        match = self.pattern.match(path)
        if match:
            return match.groupdict()
        return None
    
    async def execute_middleware_stack(self, 
                                     request: Request,
                                     response: NexioResponse, 
                                     handler: Callable = None) -> Any:
        """Execute middleware stack including the handler as the last 'middleware'."""
        stack = self.http_middlewares.copy()

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
    def __call__(self) -> tuple:
        """Return the route components for registration"""
        return self.pattern, self.handler, self.middleware
    
    def __repr__(self) -> str:
        return f"<Route {self.raw_path} methods={self.methods}>"
    

class WebsocketRoutes:
    def __init__(
        self,
        path: str,
        handler: Callable,
        middleware: Optional[Callable] = None
    ):
        assert callable(handler), "Route handler must be callable"
        self.raw_path = path
        self.handler = handler
        self.middleware = middleware
        route_info = RouteBuilder.create_pattern(path)
        self.pattern = route_info.pattern
        self.param_names = route_info.param_names
        self.route_type = route_info.route_type
        self.router_middleware = None
    
    def match(self, path: str) -> Optional[dict]:
        """
        Match a path against this route's pattern and return captured parameters
        """
        match = self.pattern.match(path)
        if match:
            return match.groupdict()
        return None
    
    async def execute_middleware_stack(self, ws, **kwargs):
        """
        Executes WebSocket middleware stack after route matching.
        """
        middleware_list = self.router_middleware or []

        stack = middleware_list.copy()
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
    def __call__(self) -> tuple:
        """Return the route components for registration"""
        return self.pattern, self.handler, self.middleware
    
    def __repr__(self) -> str:
        return f"<WSRoute {self.raw_path}>"
    


class WSRouter(BaseRouter):
    def __init__(self, prefix: Optional[str] = None):
        self.prefix = prefix or ""
        self.routes: List[WebsocketRoutes] = []
        self.middlewares: List[Callable] = []
        
        if self.prefix and not self.prefix.startswith("/"):
            warnings.warn("WSRouter prefix should start with '/'")
            self.prefix = f"/{self.prefix}"
    
    def add_route(self, route: WebsocketRoutes) -> None:
        """Add a WebSocket route with proper prefix handling"""
        if self.prefix:
            prefixed_route = WebsocketRoutes(
                f"{self.prefix}{route.raw_path}",
                route.handler,
                middleware=route.middleware
            )
            self.routes.append(prefixed_route)
        else:
            self.routes.append(route)
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the WebSocket router"""
        if callable(middleware):
            self.middlewares.append(middleware)
    
    def get_routes(self) -> List[WebsocketRoutes]:
        """Get all WebSocket routes with their patterns, handlers, and middleware"""
        routes = []
        for route in self.routes:
            route_ = WebsocketRoutes(
                path=route.raw_path, 
                handler=route.handler, 
                middleware=route.middleware
            )
            setattr(route_, "router_middleware", self.middlewares)
            routes.append(route_)
        return routes

    def ws(self, path: str) -> Callable:
        """Decorator to register a WebSocket route."""
        def decorator(handler: Callable) -> Callable:
            route = WebsocketRoutes(path, handler)
            self.add_route(route)
            return handler
        return decorator

    async def handle_websocket(self, ws, **kwargs):
        """
        Handle a WebSocket connection for all routes in this router.
        This method should be implemented by the application that uses this router.
        """
        pass

    def __repr__(self) -> str:
        return f"<WSRouter prefix='{self.prefix}' routes={len(self.routes)}>"