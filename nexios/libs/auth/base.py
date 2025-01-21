from __future__ import annotations
import typing
from urllib.parse import urlencode

_user_loader = None

def get_user_loader():
    return _user_loader

def user_loader(func):
    print(func)
    global _user_loader
    _user_loader = func
    

from nexios.http import Request,Response



class AuthenticationError(Exception):
    pass


class AuthenticationBackend:
    async def authenticate(self, req: Request,res :Response):
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
