from nexios.http import Request,Response
import typing
class BaseMiddleware:
    def __init__(self,**kwargs :typing.Dict[typing.Any,typing.Any]) -> None:
        pass
    async def __call__(self, request :Request, response :Response, next_middleware :typing.Callable[...,typing.Awaitable[None]]):
        """Call the middleware process and pass control to the next middleware in the stack."""
        result = await self.process_request(request, response)
        if result:
            
            return result
        await next_middleware()
        
        await self.process_response(request, response)
        


    async def process_request(self, request :Request, response :Response) -> typing.Any[None,Response]:
        """Override this method in child classes to process the request before passing it along."""
        pass

    async def process_response(self, request :Request, response :Response) -> typing.Any[None,Response]:
        """Override this method in child classes to process the response before returning it."""
        pass
