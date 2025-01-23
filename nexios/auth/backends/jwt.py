try:
    import jwt
except ImportError:
    raise ImportError("Please install PyJWT to use JWT authentication backend")
from typing import Optional, Tuple
from nexios.auth.base import AuthenticationBackend
from nexios.http import Request, Response
from nexios.auth.base import UnauthenticatedUser, SimpleUser
from nexios.config import get_config

def create_jwt(payload: dict, secret: str = None, algorithm: str = "HS256") -> str:
    """
    Create a JWT token.
    Args:
        payload (dict): Data to include in the token.
        secret (str): Secret key to sign the token.
        algorithm (str): Algorithm to use for signing the token.
    Returns:
        str: Encoded JWT token.
    """
    secret = secret or get_config().secret_key
    return jwt.encode(payload, secret, algorithm=algorithm)

def decode_jwt(token: str, secret: str, algorithms: list) -> dict:
    """
    Decode a JWT token.
    Args:
        token (str): Encoded JWT token.
        secret (str): Secret key used to sign the token.
        algorithms (list): List of algorithms to decode the token.
    Returns:
        dict: Decoded token payload.
    """
    try:
        return jwt.decode(token, secret, algorithms=algorithms)
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

class JWTAuthBackend(AuthenticationBackend):
    def __init__(self, authenticate_func):
        self.authenticate_func = authenticate_func
      
      

    async def authenticate(self, request: Request, response: Response) -> Optional[Tuple[str, dict]]:
        app_config = get_config()
        self.secret = app_config.secret_key
        self.algorithms = app_config.jwt_algorithms or ["HS256"]
    
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            response.headers["WWW-Authenticate"] = 'Bearer realm="Access to the API"'
            return None

        token = auth_header.split(" ")[1]
        try:
            payload = decode_jwt(token, self.secret, self.algorithms)
        except ValueError as e:

            return None

        user = await self.authenticate_func(**payload)
        if not user:
            return UnauthenticatedUser()

        return user


