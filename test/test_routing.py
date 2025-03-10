from nexios import get_application, NexiosApp
import pytest
from nexios.testing import Client
from nexios.http import Request, Response
from nexios.routing import Router, Routes

@pytest.fixture
async def async_client():
    app = get_application()  # Fresh app instance for each test
    async with Client(app, log_requests=True) as c:
        yield c, app


async def test_route_decorator(async_client):
    client, app = async_client  # Extract client and app
    
    @app.get("/get")
    async def handle_get(req: Request, res: Response):
        return res.json({"method": req.method})

    @app.post("/post")
    async def handle_post(req: Request, res: Response):
        return res.json({"method": req.method})

    # Test GET request
    get_response = await client.get("/get")
    assert get_response.status_code == 200
    assert get_response.json() == {"method": "GET"}

    # Test POST request
    post_response = await client.post("/post")
    assert post_response.status_code == 200
    assert post_response.json() == {"method": "POST"}


async def test_add_route_method(async_client):
    client, app = async_client  # Extract client and app

    async def handle_get(req: Request, res: Response):
        return res.json({"method": req.method})

    async def handle_post(req: Request, res: Response):
        return res.json({"method": req.method})

    # Add routes
    app.add_route(Routes("/get", handle_get, methods=["GET"]))
    app.add_route(Routes("/post", handle_post, methods=["POST"]))

    # Test GET request
    get_response = await client.get("/get")
    assert get_response.status_code == 200
    assert get_response.json() == {"method": "GET"}

    # Test POST request
    post_response = await client.post("/post")
    assert post_response.status_code == 200
    assert post_response.json() == {"method": "POST"}


async def test_routers_no_prefix(async_client):
    client, app = async_client

    router = Router()

    @router.get("/")
    async def handle_get(req: Request, res: Response):
        return res.text("i love you")

    app.mount_router(router)

    response = await client.get("/")
    assert response.status_code == 200


async def test_url_for_with_params(async_client):
    client, app = async_client

    @app.get("/get/name/{age}", name="name")
    async def get(req: Request, res: Response):
        ...

    url = app.url_for("name", age=0)
    assert url == "/get/name/0"
