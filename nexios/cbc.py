from nexios.http import response,request
from nexios.http.response import NexioResponse
from nexios.types import HandlerType
from typing import Any

class APIHandler:
    allowed_methods = ['get','post','delete','put','patch','options']
    async def handle_error(self, error: Exception, request: request.Request, response: response.NexioResponse) :
       pass
    async def before_request(self, request: request.Request, response: response.NexioResponse):
        
        
        pass
    
    async def after_request(self, request: request.Request, response: response.NexioResponse):
        """Hook that runs after each request"""

    async def __call__(self, request: request.Request, response:response.NexioResponse) ->  Any[HandlerType]:
        method = request.method.lower()
        if method not in self.allowed_methods:
            return response.json("Method not allowed",status_code=405)
        
        handler :HandlerType| None = getattr(self, method, None)
        if not callable(handler):
            return response.status(405)
        try:
            before_request = await self.before_request(request, response)
            if isinstance(before_request,NexioResponse): #type:ignore
                return before_request
            
            _response :HandlerType = await handler(request,response) #type:ignore
            await self.after_request(request,response)

            return _response

            
        
        except Exception as e:
            
            await self.handle_error(e,request,response)
        
