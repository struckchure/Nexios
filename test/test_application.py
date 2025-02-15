from nexios import get_application,NexiosApp
from nexios.routing import Routes,WebsocketRoutes
import pytest
from nexios.http import Request,Response

@pytest.fixture
def app() -> NexiosApp:
    return get_application()

@pytest.mark.asyncio
async def test_app_initialization(app):
    assert app.server_error_handler is None
    assert isinstance(app.routes, list)
    assert isinstance(app.ws_routes, list)
    assert isinstance(app.http_middlewares, list)
    assert isinstance(app.ws_middlewares, list)
    assert isinstance(app.startup_handlers, list)
    assert isinstance(app.shutdown_handlers, list)
    assert app.exceptions_handler is not None

@pytest.mark.asyncio
async def test_on_startup(app):
    async def startup_handler():
        pass

    app.on_startup(startup_handler)
    assert len(app.startup_handlers) == 1

@pytest.mark.asyncio
async def test_on_shutdown(app):
    async def shutdown_handler():
        pass

    app.on_shutdown(shutdown_handler)
    assert len(app.shutdown_handlers) == 1

@pytest.mark.asyncio
async def test_add_route(app):
    def handler(request: Request, response: Response):
        pass

    app.add_route(Routes("/test", handler))
    assert len(app.routes) == 1

@pytest.mark.asyncio
async def test_add_ws_route(app):
    def handler(ws):
        pass

    app.add_ws_route(WebsocketRoutes("/ws", handler))
    assert len(app.ws_routes) == 1

@pytest.mark.asyncio
async def test_add_middleware(app):
    async def middleware(request: Request, response: Response, call_next):
        pass

    app.add_middleware(middleware)
    assert len(app.http_middlewares) > 1

@pytest.mark.asyncio
async def test_add_ws_middleware(app):
    async def ws_middleware(ws, call_next):
        pass

    app.add_ws_middleware(ws_middleware)
    assert len(app.ws_middlewares) == 1

@pytest.mark.asyncio
async def test_route_decorator(app):
    @app.route("/test")
    async def handler(request: Request, response: Response):
        pass

    assert len(app.routes) == 1

    