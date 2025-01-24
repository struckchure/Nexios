import secrets
from nexios.middlewares.base import BaseMiddleware
from nexios.http import Request,Response
from nexios.config import get_config

class CSRFMiddleware(BaseMiddleware):
    """
    Middleware to protect against Cross-Site Request Forgery (CSRF) attacks.
    """
    def __init__(self, *kwargs):
        self.app_config = get_config()
        self.CSRF_TOKEN_NAME = self.app_config.csrf_token or "csrf_token"
        super().__init__(*kwargs)


    async def process_request(self, request: Request, response :Response):
        """
        Process the incoming request to validate the CSRF token for unsafe HTTP methods.
        """
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            
            csrf_token = request.session.get_session(self.CSRF_TOKEN_NAME)

            # Check if the token is missing or invalid
            if not csrf_token or not self._validate_token(request, csrf_token):
                return response.send("Invalid CSRF Token",status_code=403)

        self._ensure_csrf_token_in_session(request)
        response.delete_cookie(self.CSRF_TOKEN_NAME)
    def _validate_token(self, request: Request, csrf_token: str) -> bool:
        """
        Validate the CSRF token from the request against the stored session token.
        """
        request_token = (
            request.headers.get("X-CSRF-Token") or
            request.cookies.get(self.CSRF_TOKEN_NAME)
        )
        return secrets.compare_digest(csrf_token, request_token or "")

    def _ensure_csrf_token_in_session(self, request: Request):
        """
        Ensure a CSRF token exists in the session; if not, generate a new one.
        """
        session = request.session.get_session(self.CSRF_TOKEN_NAME)
        if not session:
            request.session.set_session(self.CSRF_TOKEN_NAME, secrets.token_hex(32))

    async def process_response(self, request: Request, response):
        """
        Inject the CSRF token into the response for client-side usage.
        """
        session = request.session
        csrf_token = session.get_session(self.CSRF_TOKEN_NAME)
        if csrf_token:
            response.set_cookie(self.CSRF_TOKEN_NAME, csrf_token, httponly=True)
        return response
