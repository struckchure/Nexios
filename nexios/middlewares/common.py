from nexios.middlewares.base import BaseMiddleware
from nexios.http.response import NexioResponse
from nexios.http.request import Request
from typing_extensions import Annotated, Doc


class CommonMiddleware(BaseMiddleware):
    """
    Middleware for applying common security and response headers.

    This middleware ensures that every response includes essential security headers,
    such as `X-Frame-Options`, `X-XSS-Protection`, and `Strict-Transport-Security`.

    It also sets `Cache-Control` to `no-store` to prevent caching of sensitive data.
    """

    async def process_request(
        self,
        request: Annotated[
            Request,
            Doc("The incoming HTTP request."),
        ],
        response: Annotated[
            NexioResponse,
            Doc("The response object that can be modified before processing."),
        ],
    ) -> None:
        """
        Process the incoming request before it reaches the route handler.

        This method currently does nothing but can be extended for
        additional pre-processing logic.

        Args:
            request (Request): The incoming HTTP request.
            response (NexioResponse): The response object (not modified here).

        Returns:
            None
        """
        pass

    async def process_response(
        self,
        request: Annotated[
            Request,
            Doc("The HTTP request associated with the response."),
        ],
        response: Annotated[
            NexioResponse,
            Doc("The response object that is modified before being sent."),
        ],
    ) -> NexioResponse:
        """
        Process the outgoing response and add common security headers.

        This method ensures that the response includes security and
        cache-control headers to enhance security and prevent unwanted
        data exposure.

        Args:
            request (Request): The HTTP request object.
            response (NexioResponse): The response object to be modified.

        Returns:
            NexioResponse: The modified response with additional headers.
        """
        response.headers["Content-Type"] = "application/json"

        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        response.headers["Cache-Control"] = "no-store"

        if request.user_agent:
            response.headers["X-User-Agent"] = request.user_agent

        return response
