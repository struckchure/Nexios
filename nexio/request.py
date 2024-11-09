from starlette.requests import Request as RequestObject
from starlette.types import Scope,Receive,Send
import typing

class Request:

    def __init__(self, scope :Scope, 
                 recieve :Receive, 
                 send :Send) -> None:
        
        self._request = RequestObject(
            scope=scope,
            receive=recieve,
            send=send
        )

        self.headers = self._request.headers
        self.cookies = self._request.cookies
        self.client = self._request.client

    @property
    def url(self):
        return self._request.url 
    
    @property
    def _meta_data(self):
        return self._request.scope
    @property
    def meta(self):
        return self._request.scope,self._request.receive,self._request._send
    @property
    def method(self):
        return self._request.method
    
    @property
    def base_url(self):
        return self._request.base_url
    
    @property
    def is_secured(self):
        return self._request.url.scheme == "https"
    

    #TODO : Add type called path
    def build_absoulte_uri(self, path :str) -> str:
        assert isinstance(path, str)
        return str(self.base_url)+path
    

    @property
    def auth(self) -> typing.Any:
        assert (
            "auth" in self.scope
        ), "AuthenticationMiddleware must be installed to access request.auth"
        return self.scope["auth"]

    @property
    def user(self) -> typing.Any:
        assert (
            "user" in self.scope
        ), "AuthenticationMiddleware must be installed to access request.user"
        return self.scope["user"]
    
    @property
    def session(self) -> typing.Dict[str, typing.Any]:
        assert (
            "session" in self.scope
        ), "SessionMiddleware must be installed to access request.session"
        return self.scope["session"]
    

    @property
    def query_params(self):
        return self._request.query_params._dict 
    


    async def data(self) -> typing.Dict[str,any]:
        data = {}

        try:
            json_data = await self._request.json()
            if isinstance(json_data,dict):
                data.update(data)

        except Exception as e:
            pass

        try:
            form_data = await self._request.form()
            data.update(form_data)

        except Exception as e:
            pass