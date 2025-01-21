from __future__ import annotations

import inspect

from .base import (
    AuthenticationBackend,
    UnauthenticatedUser,
)
from nexios.middlewares.base import BaseMiddleware
from nexios.http import Request,Response

class AuthenticationMiddleware(BaseMiddleware):
   def __init__(self, backend: AuthenticationBackend) -> None:
       self.backend = backend

   async def process_request(self, request: Request, response: Response):
        
        if not inspect.iscoroutinefunction(self.backend.authenticate):
            user = self.backend.authenticate(request,response)
        else:
            user = await self.backend.authenticate(request,response)
        if user is None:
            request.user = UnauthenticatedUser()

        request.user = user
         
