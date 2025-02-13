import traceback
import logging
import typing
from nexios.http.request import Request
from nexios.http.response import NexioResponse
from .base import BaseMiddleware
# Setting up a logger for middleware
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
# You can also configure more advanced logging handlers (e.g., logging to a file, database, or external service).

class ErrorHandlerMiddleware(BaseMiddleware):
    """
    A middleware class for handling errors globally within the application.
    This class processes requests and responses, capturing errors and logging them.
    """

    def __init__(self, *args :typing.List[typing.Any], **kwargs :typing.Dict[str,typing.Any]) -> None:
        super().__init__(*args, **kwargs)
        # Any additional initialization can be done here
        self.error_status_code = 500
        self.error_message = "An unexpected error occurred"



    async def __call__(self, request: Request, response: NexioResponse, next_middleware: typing.Callable[...,typing.Awaitable[None]]) -> NexioResponse:
        """
        The core method of the middleware, which processes the request, handles the error, and processes the response.
        """
        try:

           await next_middleware()
        except Exception as _:
            # Capture and log the exception details
            self._log_error(traceback.format_exc())


            return  response.send("Server error",status_code=500,headers= {
            "Access-Control-Allow-Origin": request.origin or "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "content-type",
            "Access-Control-Allow-Credentials":"true"
        })


        return response

    def _log_error(self, error:str) -> None:
        """
        A helper method to log the error details in a structured and configurable way.
        This can be expanded to log to files, external monitoring services, etc.
        """
        # Log the error with traceback for full context
        logger.error(f"Unhandled exception: {str(error)}")
        logger.debug("Error traceback: %s", traceback.format_exc())
