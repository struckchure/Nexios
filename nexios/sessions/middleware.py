from nexios.middlewares.base import BaseMiddleware
from .signed_cookies import SignedSessionManager
from .file import FileSessionManager
from .db import DBSessionManager
from .base import BaseSessionInterface
from nexios.http.request import Request
from nexios.http.response import NexioResponse
from nexios.config import get_config
class SessionMiddleware(BaseMiddleware):

    async def process_request(self, request :Request, response):
    
        self.config = get_config().session
        if self.config:
            session_cookie_name = self.config.session_cookie_name
        else:
            session_cookie_name =  "session_id"

        self.session_cookie_name = session_cookie_name
        managers = {
            "file":FileSessionManager,
            "db":DBSessionManager,
            "cookies":SignedSessionManager
        }    
        if self.config:
            manager_config = self.config.session_manager 
        else:
            manager_config  = "cookies"
        
        manager :BaseSessionInterface = managers.get(manager_config,SignedSessionManager)
        session = manager(session_key=request.cookies.get(session_cookie_name))
        await session.load()
        # request.scope['session'] = session
        request.session = session
        print("Request before controller")

    async def process_response(self, request :Request , response :NexioResponse):
        
        if request.session.is_empty() and request.session.accessed:
            response.delete_cookie(
                key= self.session_cookie_name
                
                )
            return 
        print("Before respnse retuen check",request.session.modified)
        if request.session.should_set_cookie:
            await request.session.save()

            session_key = request.session.get_session_key()

            response.set_cookie(
                key =  self.session_cookie_name,
                value=session_key,
                domain=request.session.get_cookie_domain(),
                path=request.session.get_cookie_path(),
                httponly=request.session.get_cookie_httponly(),
                secure=request.session.get_cookie_secure(),
                samesite=request.session.get_cookie_samesite(),
                expires=request.session.get_expiration_time()
                
            )
        

