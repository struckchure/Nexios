from nexios import get_application, NexioApp
from nexios.exceptions import HTTPException
from nexios.http import Request, Response
from nexios.http.response import Response
from nexios.routing import Router, Routes, WSRouter
from typing import Callable, Any
from nexios.websockets import WebSocket
from nexios.hooks import before_request
from nexios.testing.transport import NexiosAsyncTransport
from nexios.testing.client import Client
import httpx
import asyncio
import pytest

test_router = Router()


async def handle_server_error(req: Request, res: Response, exc: Exception):
    return res.json({"err": "Hello"})


class NotFound(HTTPException):
    pass


app: NexioApp = get_application()

import httpx
import asyncio



async def handler_not_found(request: Request, response: Response, exc: Exception):
    print(request.path)
    return response.json({"ERROR": "not found"})


app.add_exception_handler(404, handler_not_found)


async def my_jook(request: Request, response: Response) -> Any:
    print("out hook")
    return response.json({"hello": "hi"})


@before_request(my_jook)
async def index(req: Request, res: Response) -> Response:
    # raise RecursionError("Vale error")
    return res.json({"text": "Helloo world"})


ws_router = WSRouter()


@ws_router.ws_route("/chat")
async def ws(ws: WebSocket):
    await ws.accept()


async def my_middleware(
    request: Request, response: Response, call_next: Callable[..., Any]
):
    response.text("Hello")
    await call_next()


app.add_middleware(my_middleware)
app.add_route(Routes("", index))
app.mount_router(test_router)
app.mount_ws_router(ws_router)

@pytest.mark.asyncio
async def test_index():
    async with Client(app=app,base_url="http://test") as client:
        response = await client.get("")
        assert response.status_code == 200
        assert response.json() == {"text": "Helloo world"}

# asyncio.run(main())