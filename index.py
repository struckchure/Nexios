from nexios import get_application,NexioApp
from nexios.exceptions import HTTPException
from nexios.http import Request,Response
from nexios.routing import Router,Routes,WSRouter
from typing import Callable,Any
from nexios.websockets import WebSocket
test_router = Router()
async def handle_server_error(req :Request,res :Response,exc :Exception):
    return res.json({"err":"Hello"})

class NotFound(HTTPException):
    pass
app :NexioApp = get_application()
async def handler_not_found(request: Request,response:Response, exc: Exception):
    return response.json({"ERROR":"not found"})
    
app.add_exception_handler(ValueError,handler_not_found)
async def index(req:Request, res:Response) -> Response:
    # raise RecursionError("Vale error")
    return res.json({"text":"Helloo world"})
ws_router = WSRouter()
@ws_router.ws_route("/chat")
async def ws(ws:WebSocket):
    await ws.accept()
    
async def my_middleware(request:Request, response:Response,call_next:Callable[...,Any]):
    await call_next()
    return response.text("Hello")
app.add_middleware(my_middleware)
app.add_route(Routes("",index))
app.mount_router(test_router)
app.mount_ws_router(ws_router)
