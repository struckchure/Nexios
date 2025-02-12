from nexios.http import Request, Response
import typing
from typing_extensions import Annotated, Doc


class BaseMiddleware:
    """
    Base middleware class for handling request-response processing in Nexios.

    This class provides a structure for middleware in the Nexios framework.
    It allows child classes to intercept and modify HTTP requests before they
    reach the main application logic and modify responses before they are returned
    to the client.

    Middleware classes inheriting from `BaseMiddleware` should implement:

    - `process_request()`: To inspect, modify, or reject an incoming request.
    - `process_response()`: To inspect or modify an outgoing response.

    If `process_request` returns a `Response`, the request cycle is short-circuited,
    and the response is immediately sent back to the client. Otherwise, control is
    passed to the next middleware in the stack.
    """

    def __init__(
        self,
        **kwargs: Annotated[
            typing.Dict[typing.Any, typing.Any],
            Doc("Additional keyword arguments for middleware configuration."),
        ],
    ) -> None:
        """
        Initializes the middleware with optional keyword arguments.

        Middleware can accept configuration parameters via `kwargs`. These parameters
        can be used to modify behavior when subclassing this base class.

        Args:
            **kwargs (dict): Arbitrary keyword arguments for middleware settings.
        """
        pass

    async def __call__(
        self,
        request: Annotated[
            Request,
            Doc("The incoming HTTP request object representing the client request."),
        ],
        response: Annotated[
            Response,
            Doc("The HTTP response object that will be returned to the client."),
        ],
        next_middleware: Annotated[
            typing.Callable[..., typing.Awaitable[None]],
            Doc("The next middleware function in the processing chain."),
        ],
    ) -> Annotated[
        typing.Optional[Response],
        Doc(
            "If `process_request` returns a response, it short-circuits the request cycle, "
            "and the returned response is sent to the client immediately. Otherwise, `None` is returned."
        ),
    ]:
        """
        Handles the request-response cycle for the middleware.

        This method does the following:
        1. Calls `process_request()` to inspect or modify the request before passing it forward.
        2. If `process_request()` returns a response, the cycle stops, and the response is returned.
        3. Otherwise, it calls `next_middleware()`, allowing the request to proceed.
        4. After the request has been processed, it calls `process_response()` to modify the response.

        Args:
            request (Request): The incoming HTTP request object.
            response (Response): The outgoing HTTP response object.
            next_middleware (Callable[..., Awaitable[None]]): A function representing the next middleware.

        Returns:
            Optional[Response]: A `Response` object if `process_request` terminates the request early.
        """
        result = await self.process_request(request, response)
        if result:
            return result

        await next_middleware()

        await self.process_response(request, response)

    async def process_request(
        self,
        request: Annotated[
            Request, Doc("The HTTP request object that needs to be processed.")
        ],
        response: Annotated[
            Response,
            Doc("The HTTP response object that will be modified before returning."),
        ],
    ) -> Annotated[
        typing.Optional[Response],
        Doc(
            "If this method returns a Response, it stops the middleware chain, and the response is sent immediately. "
            "Otherwise, it returns `None`, allowing the request to continue."
        ),
    ]:
        """
        Hook for processing an HTTP request before passing it forward.

        Override this method in subclasses to inspect, modify, or reject requests before
        they reach the next middleware or the application logic.

        Args:
            request (Request): The incoming HTTP request object.
            response (Response): The outgoing HTTP response object.

        Returns:
            Optional[Response]: A `Response` object if the request cycle should be terminated early. Otherwise, `None`.
        """
        pass

    async def process_response(
        self,
        request: Annotated[
            Request,
            Doc(
                "The original HTTP request object, available for context during response processing."
            ),
        ],
        response: Annotated[
            Response,
            Doc(
                "The HTTP response object that can be modified before sending to the client."
            ),
        ],
    ) -> Annotated[
        typing.Optional[Response],
        Doc(
            "If this method returns a Response, it replaces the existing response before reaching the client. "
            "Otherwise, it returns `None`, allowing the response to be sent as is."
        ),
    ]:
        """
        Hook for processing an HTTP response before returning it to the client.

        Override this method in subclasses to modify response headers, content, or status codes
        before they are sent back to the client.

        Args:
            request (Request): The original HTTP request object.
            response (Response): The outgoing HTTP response object.

        Returns:
            Optional[Response]: A modified `Response` object if the middleware needs to alter the final response.
        """
        pass
