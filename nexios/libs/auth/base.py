from __future__ import annotations
import typing
from urllib.parse import urlencode



from starlette._utils import is_async_callable
from starlette.exceptions import HTTPException
from nexios.http import Request,Response
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket


class AuthenticationError(Exception):
    pass


class AuthenticationBackend:
    async def authenticate(self, req: Request):
        raise NotImplementedError() 




class BaseUser:
    @property
    def is_authenticated(self) -> bool:
        raise NotImplementedError() 

    @property
    def display_name(self) -> str:
        raise NotImplementedError() 

    @property
    def identity(self) -> str:
        raise NotImplementedError() 


class SimpleUser(BaseUser):
    def __init__(self, username: str) -> None:
        self.username = username

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username


class UnauthenticatedUser(BaseUser):
    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def display_name(self) -> str:
        return ""
