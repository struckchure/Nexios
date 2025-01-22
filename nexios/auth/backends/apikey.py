from typing import Optional, Tuple
from nexios.auth.base import AuthenticationBackend
from nexios.http import Request, Response
from nexios.auth.base import UnauthenticatedUser
from nexios.auth.base import get_user_loader

class APIKeyAuthBackend(AuthenticationBackend):

    def __init__(self, authenticate_func, header_name: str = "X-API-Key"):
        """
        Initializes the APIKeyAuthBackend with the provided authentication function and optional header name.
        
        :param authenticate_func: Function that takes an API key and returns a user if valid, None otherwise.
        :param header_name: The header name where the API key is expected (default is "X-API-Key").
        """
        self.authenticate_func = authenticate_func
        self.header_name = header_name

    async def authenticate(self, request: Request, response: Response) -> Optional[Tuple[str, dict]]:
        """
        Authenticates the request by checking for an API key in the specified header.
        
        :param request: The incoming HTTP request.
        :param response: The response object to modify (e.g., setting headers).
        :return: A tuple of (username, user_data) or None if authentication fails.
        """
        # Retrieve the API key from the header
        api_key = request.headers.get(self.header_name)
        if not api_key:
            response.headers["WWW-Authenticate"] = f'APIKey realm="Access to the API"'
            return None

        # Authenticate the API key
        user = await self.authenticate_func(api_key)
        if not user:
            return UnauthenticatedUser()

        return user
