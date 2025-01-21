import base64,inspect
from typing import Optional, Tuple
from nexios.libs.auth.base import AuthenticationBackend
from nexios.config import app_config
from nexios.http import Request, Response
from nexios.libs.auth.base import UnauthenticatedUser,SimpleUser
from nexios.libs.auth.base import get_user_loader
class BasicAuthBackend(AuthenticationBackend):

 
    async def authenticate(self, request :Request, response :Response) -> Optional[Tuple[str, dict]]:
       
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            response.headers["WWW-Authenticate"] = 'Basic realm="Access to the API"'
            return None

        
        try:
            encoded_credentials = auth_header.split(" ")[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)
        except (ValueError, base64.binascii.Error):
            return None

        #
        user = await self.validate_user(username, password)
        if not user:
           return UnauthenticatedUser()

        return user
    async def validate_user(self, username: str, password: str) -> Optional[dict]:
        user_loader = get_user_loader()
        if user_loader:
            if inspect.iscoroutinefunction(user_loader):
                user = await user_loader(username,password)
                return user
            user = user_loader(username,password)
            return user
        
        return None
