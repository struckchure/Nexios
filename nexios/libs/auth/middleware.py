from __future__ import annotations

import typing

from .base import (
    AuthenticationBackend,
    UnauthenticatedUser,
)
from nexios.middlewares.base import BaseMiddleware
from nexios.http import Request,Response

class AuthenticationMiddleware(BaseMiddleware):
   def __init__(self, backend: AuthenticationBackend) -> None:
       self.backend = backend

   def process_request(self, request: Request, response: Response):
        if request.user.is_authenticated:
            return

        user = self.backend.authenticate(request)
        if user is None:
            request.user = UnauthenticatedUser()

        request.user = user
         
