#type:ignore
from __future__ import annotations

import inspect

from .base import (
    AuthenticationBackend,
    UnauthenticatedUser,
    BaseUser
)
from nexios.middlewares.base import BaseMiddleware
from nexios.http import Request,Response

class AuthenticationMiddleware(BaseMiddleware):
   def __init__(self, backend: AuthenticationBackend) -> None:
       self.backend = backend

   async def process_request(self, request: Request, response: Response):
        
        if not inspect.iscoroutinefunction(self.backend.authenticate):
            user:BaseUser = self.backend.authenticate(request,response) 
        else:
            user:BaseUser = await self.backend.authenticate(request,response)
        if user is None:
            request.user = UnauthenticatedUser()

        request.scope["user"] = user
         
