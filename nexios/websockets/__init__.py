from .base import WebSocket
from nexios.types import Scope,Send,Receive
async def get_websocket_session(scope :Scope,receive :Receive, send :Send ) -> WebSocket:
    ws = WebSocket(scope,receive,send)
    return ws 

