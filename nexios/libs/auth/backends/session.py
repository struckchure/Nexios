import time
from typing import Optional, Tuple
from nexios.libs.auth.base import AuthenticationBackend
from nexios.http import Request, Response
from nexios.libs.auth.base import UnauthenticatedUser
from nexios.config import app_config
from nexios.libs.auth.base import get_user_loader

class SessionAuthBackend(AuthenticationBackend):

    def __init__(self, authenticate_func):
        """
        Initializes the SessionAuthBackend with session authentication settings.
        
        :param authenticate_func: Function that takes a session_id and returns a user if valid, None otherwise.
        :param session_timeout_key: The setting name for the session timeout in `app_config`.
        """
        self.authenticate_func = authenticate_func
        

    async def authenticate(self, request: Request, response: Response) -> Optional[Tuple[str, dict]]:
        self.session_timeout_key = app_config.session_auth.session_timeout_key or "session_timeout"
        self.session_timeout = app_config.session_auth.session_timeout or 3600
        """
        Authenticates the request by checking for a valid session.
        
        :param request: The incoming HTTP request.
        :param response: The response object to modify (e.g., setting headers).
        :return: A tuple of (username, user_data) or None if authentication fails.
        """
        session_id = request.cookies.get('session_id') or request.headers.get('X-Session-ID')
        
        if not session_id:
            response.headers["WWW-Authenticate"] = 'Session realm="Access to the API"'
            return None
        
        session_data = await self.authenticate_func(session_id)
        
        if not session_data:
            return UnauthenticatedUser()

        current_time = time.time()
        
        new_expiry_time = current_time + self.session_timeout
        session_data["expiry_time"] = new_expiry_time
        await self.authenticate_func.update_session(session_id, session_data)

        return session_data["user"]

