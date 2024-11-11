from typing import Any, List
from typing import Callable, Union
import re

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
        self.routes.append(route)

    def get_routes(self) ->List[tuple[str,Callable]]:
        return self.routes


    def __repr__(self):
        return f"<Nexio Route prefix = {self.prefix} >"

    
        



class Routes:

    def __init__(self, route,handler,middleware = None):
        assert callable(handler), "Route handler most be callable"
        path_regex = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", route)
        
        self.route, self.handler,self.middleware = re.compile(f"^{path_regex}$"), handler, middleware

    def __call__(self) -> List[tuple[str,Callable]]:

        return (self.route, self.handler, self.middleware)