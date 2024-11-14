from abc import ABC, abstractmethod
import traceback
import typing
from nexio.http.request import Request
from nexio.http.response import NexioResponse

class BaseMiddleware(ABC):
    """
    Base middleware class that defines the interface for all middleware classes.
    Provides hooks for processing requests before and after the handler.
    """
    
    async def __call__(self, request: Request, response: NexioResponse, call_next: typing.Callable):
        """
        Main entry point for middleware execution.
        Coordinates the request/response cycle.
        """
        try:
            # Process request (pre-handler)
            await self.process_request(request, response)
            
            # Call the next middleware/handler in the chain
            response = await call_next()
            
            # Process response (post-handler)
            processed_response = await self.process_response(request, response)
            return processed_response
            
        except Exception as e:
            # Handle any errors that occur during middleware execution
            return await self.process_exception(request, response, e)
    
    @abstractmethod
    async def process_request(self, request: Request, response: NexioResponse) -> None:
        """
        Process the request before it reaches the handler.
        Override this method to implement custom request processing.
        """
        pass
    
    @abstractmethod
    async def process_response(self, request: Request, response: NexioResponse) -> NexioResponse:
        """
        Process the response after it leaves the handler.
        Override this method to implement custom response processing.
        """
        return response
    
    async def process_exception(self, request: Request, response: NexioResponse, exc: Exception) -> NexioResponse:
        """
        Handle exceptions that occur during middleware execution.
        Override this method to implement custom error handling.
        """
        return response

class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Error handling middleware that catches and processes exceptions.
    """
    
    async def process_request(self, request: Request, response: NexioResponse) -> None:
        """Set default cookie before processing request"""
        response.cookie(key="name", value="dunami")
    
    async def process_response(self, request: Request, response: NexioResponse) -> NexioResponse:
        """Pass through the response unchanged"""
        return response
    
    async def process_exception(self, request: Request, response: NexioResponse, exc: Exception) -> NexioResponse:
        """Handle any exceptions that occur during request processing"""
        error_details = traceback.format_exc()
        print(error_details)  # You might want to use proper logging here
        
        response.status(500)
        return response

