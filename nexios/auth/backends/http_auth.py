import base64
from typing import Any,Callable,Awaitable
from nexios.auth.base import AuthenticationBackend
from nexios.http import Request, Response
from nexios.auth.base import UnauthenticatedUser
class BasicAuthBackend(AuthenticationBackend):

    def __init__(self,authenticate_func:Callable[...,Awaitable[Any]]):
        self.authenticate_func = authenticate_func

    async def authenticate(self, request :Request, response :Response) -> Any: #type:ignore
       
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            response.headers["WWW-Authenticate"] = 'Basic realm="Access to the API"'
            return None

        
        try:
            encoded_credentials = auth_header.split(" ")[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)
        except (ValueError, base64.binascii.Error):#type:ignore
            return None

        
        user :Any= await self.authenticate_func(username, password)
        if not user:
           return UnauthenticatedUser()

        return user
    