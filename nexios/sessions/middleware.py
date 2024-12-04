from nexios.middlewares.base import BaseMiddleware
from .signed_cookies import SignedSessionManager
from nexios.http.request import Request
from nexios.http.response import NexioResponse
class SessionMiddleware(BaseMiddleware):

    async def process_request(self, request :Request, response):
        self.config = request.scope['config']
        session_cookie_name = self.config.SESSION_COOKIE_NAME or "session_id"
        print(request.cookies)
        session = SignedSessionManager(
            config=self.config,
            session_key=request.cookies.get(session_cookie_name)

        )

        await session.load()
        request.session = session

    async def process_response(self, request :Request , response :NexioResponse):
        if request.session.modified:
            await request.session.save()

            session_key = request.session.get_session_key()

            response.set_cookie(
                key = self.config.SESSION_COOKIE_NAME or "session_id",
                value=session_key
            )

