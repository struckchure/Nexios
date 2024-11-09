from typing import Any, Awaitable, Callable, Mapping, Sequence,List,Union
from .request import Request
from .response import CustomResponse
from starlette.responses import JSONResponse
import re
from .types import HTTPMethod
from .decorators import AllowedMethods
from .routers import Router,Routes

class NexioHTTPApp:

    #TODO :Custom type for handles
    routes :List[str] = []
    middlewares :List = []
    start_function :Callable
    

    def __init__(self):
        pass 


    def on_start(self, func :Callable):
        self.start_function = func


    
    async def execute_middleware_stack(self,request: Request,
                                 response: CustomResponse, 

                                 middleware: Callable, 

                                 handler: Callable, **kwargs):
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
    async def handle_request(self,scope, receive, send):
        request = Request(scope, receive,send)
        response = CustomResponse()

        for path_pattern, handler , middleware, in self.routes:
            match = path_pattern.match(request.url.path)
            if match:
                kwargs = match.groupdict()
                # await middleware(await handler(request, response, **kwargs))
                try:
                    await self.execute_middleware_stack(request,
                                                  response,
                                                  middleware,
                                                  handler)
                except Exception as e:
                    error_response =    JSONResponse({"error":str(e)},
                                                     status_code=500)
                    await error_response(scope,receive,send)
                await response(scope, receive, send)
                return

        error_response = JSONResponse({"error": "Not found"}, status_code=404)
        await error_response(scope, receive, send)

    def route(self, path: str, methods: List[Union[str, HTTPMethod]] = None):
        """
        Route decorator that combines path routing with method restrictions
        """
        def decorator(handler: Callable):
            middlewares = []
            if methods:
                middlewares.append(AllowedMethods(methods))
            self.add_route(path, handler, middlewares)
            return handler
        return decorator

    def add_route(self, route :Routes):
       route,handler,middleware = route()
       self.routes.append((route,handler,middleware))

        
        


    def add_middleware(self, middleware):
        if callable(middleware):
            self.middlewares.append(middleware)

    async def __call__(self, scope, receive, send) -> Any:
       
        if callable(self.start_function):
            self.start_function()
        if scope['type'] == 'http':    
            await self.handle_request(scope, receive, send)
        else:
            pass


    

    
    def mount_router(self, router :Router):
        for route in router.get_routes():
            
            self.add_route(route)