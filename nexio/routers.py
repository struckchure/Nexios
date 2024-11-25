from typing import Any, List
from typing import Callable, Union
import re,warnings

class BaseRouter:

    def add_route(self):

        raise NotImplemented("Not implemented")
    
    def routes(self):

        raise NotImplemented("Not implemented")
    

    def add_middleware(self):

        raise NotImplemented("Not implemented")


class Router(BaseRouter):
    routes: List[tuple[str, str, Callable]] = []

    def __init__(self, prefix :str = None) -> None:
        self.prefix = prefix

    def __call__(self,*args,**kwargs) -> Any:
        return self.routes 
    
    def add_route(self, route :"Routes") -> None:
        if not self.prefix:
            self.routes.append(route)
            return
    
        if not self.prefix.startswith("/"):
            warnings.warn("Routes path should start with '/' ")

        route_ = Routes(f"{self.prefix}{route.raw_route}",
                        route.handler,
                        middleware=route.middleware)
        self.routes.append(route_)

    def get_routes(self) ->List[tuple[str,Callable]]:
        return self.routes


    def __repr__(self):
        return f"<Nexio Route prefix= {self.prefix} >"

    
        
class Routes:
    router_prefix = None

    def __init__(self, route,handler,middleware = None):
        assert callable(handler), "Route handler most be callable"
        self.path_regex = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", route)
        self.raw_route = route 
        #To allow the router to be able to access the router prefix
        self.route, self.handler,self.middleware = re.compile(f"^{self.path_regex}$"), handler, middleware

    def __call__(self) -> List[tuple[str,Callable]]:

        return (self.route, self.handler, self.middleware)